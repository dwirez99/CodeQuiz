import os
import requests
import logging

JUDGE0_API_URL = os.environ.get("JUDGE0_API_URL", "http://judge0:2358")
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import traceback
from .models import Problem, Submission

# Configure logger
logger = logging.getLogger(__name__)

# --- Judge0 API Configuration ---
# IMPORTANT: Store these securely in your environment variables, not in the code.
JUDGE0_API_URL = os.environ.get("JUDGE0_API_URL", "http://judge0:2358")
JUDGE0_API_KEY = os.environ.get("JUDGE0_API_KEY")
JUDGE0_API_HOST = os.environ.get("JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")


def call_judge0_api(code, language_id, stdin=None, expected_output=None):
    api_url = f"{JUDGE0_API_URL}/submissions?base64_encoded=false&wait=true"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": stdin,
        "expected_output": expected_output,
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        result_data = response.json()
        
        # Check for Judge0 internal errors and provide helpful messages
        if result_data.get('status', {}).get('id') == 13:  # Internal Error
            error_msg = result_data.get('message', 'Unknown internal error')
            if 'No such file or directory' in error_msg:
                # Fallback to simple Python execution for demonstration
                if language_id == 71:  # Python 3
                    return execute_python_fallback(code, stdin)
                return {
                    "success": False, 
                    "error": "Code execution environment is not properly configured. Judge0 container needs additional setup.",
                    "judge0_error": error_msg
                }
            else:
                return {
                    "success": False, 
                    "error": f"Judge0 internal error: {error_msg}",
                    "judge0_error": error_msg
                }
        
        return {"success": True, "data": result_data}
    except requests.exceptions.RequestException as e:
        logger.error(f"Judge0 API request failed: {e}")
        logger.error(f"Response content: {response.content if 'response' in locals() else 'No response'}")
        traceback.print_exc()
        # Fallback to simple Python execution for demonstration
        if language_id == 71:  # Python 3
            return execute_python_fallback(code, stdin)
        return {"success": False, "error": f"Judge0 API connection failed: {e}"}


def execute_python_fallback(code, stdin=None):
    """
    Simple Python code execution fallback when Judge0 is not working.
    WARNING: This is not secure and should only be used for development/demonstration.
    """
    import subprocess
    import tempfile
    import os
    
    try:
        # Prepare input - if stdin is None or empty but code uses input(), provide some default
        input_data = stdin if stdin is not None else ""
        
        # If input is empty but code contains input() function, provide newlines to prevent EOF
        if not input_data.strip() and 'input(' in code:
            # Count how many input() calls are in the code (rough estimation)
            input_count = code.count('input(')
            input_data = '\n' * input_count  # Provide empty lines for each input()
        
        # Create a temporary file for the Python code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute the Python code
        cmd = ['python3', temp_file]
        result = subprocess.run(
            cmd, 
            input=input_data, 
            text=True, 
            capture_output=True, 
            timeout=10  # 10 second timeout
        )
        
        # Clean up
        os.unlink(temp_file)
        
        # Clean the output - remove trailing newlines and whitespace
        stdout_clean = result.stdout.rstrip('\n\r ') if result.stdout else ""
        stderr_clean = result.stderr.rstrip('\n\r ') if result.stderr else ""
        
        return {
            "success": True, 
            "data": {
                "stdout": stdout_clean,
                "stderr": stderr_clean,
                "status": {"id": 3 if result.returncode == 0 else 4, "description": "Accepted" if result.returncode == 0 else "Wrong Answer"},
                "time": "0.1",  # Mock execution time
                "memory": 1024  # Mock memory usage
            }
        }
    except subprocess.TimeoutExpired:
        if 'temp_file' in locals():
            os.unlink(temp_file)
        return {
            "success": True, 
            "data": {
                "stdout": "",
                "stderr": "Time Limit Exceeded",
                "status": {"id": 5, "description": "Time Limit Exceeded"},
                "time": "10.0",
                "memory": 0
            }
        }
    except Exception as e:
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file)
            except:
                pass
        return {
            "success": True, 
            "data": {
                "stdout": "",
                "stderr": f"Execution Error: {str(e)}",
                "status": {"id": 11, "description": "Runtime Error"},
                "time": "0.0",
                "memory": 0
            }
        }


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])  # No authentication required
@permission_classes([AllowAny])  # Allow unauthenticated access
def run_code(request, problem_id):
    """
    Runs code with custom input without creating a final submission.
    """
    try:
        # Handle JSON data from JavaScript
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            code = data.get('code')
            language_id = data.get('language_id')
            custom_input = data.get('input')
        else:
            # Handle form data
            code = request.data.get('code')
            language_id = request.data.get('language_id')
            custom_input = request.data.get('input')
        
        logger.info(f"Received code execution request: code_length={len(code) if code else 0}, language_id={language_id}, has_input={bool(custom_input)}")

        if not code or not language_id:
            return Response({'success': False, 'error': 'Code and language are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Run with custom input if provided
        result = call_judge0_api(code, language_id, stdin=custom_input)
        logger.info(f"Judge0 API result: {result}")

        if not result['success']:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = result['data']
        # Combine compile error and runtime error for simplicity
        error_output = data.get('stderr') or data.get('compile_output')
        
        # Clean the output - remove trailing newlines and whitespace
        clean_output = data.get('stdout').rstrip('\n\r ') if data.get('stdout') else ""

        return Response({
            'success': True,
            'output': clean_output,
            'error': error_output,
            'status': data.get('status', {}).get('description', 'Unknown'),
            'execution_time': data.get('time'),
            'memory': data.get('memory'),
        })
    except Exception as e:
        logger.error(f"Error in run_code: {e}")
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])  # No authentication required for testing
@permission_classes([AllowAny])  # Allow unauthenticated access
def submit_solution(request, problem_id):
    """
    Submits a solution, runs it against all test cases, and records the result.
    """
    try:
        # Handle JSON data from JavaScript
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            code = data.get('code')
            language_id = data.get('language_id')
        else:
            # Handle form data
            code = request.data.get('code')
            language_id = request.data.get('language_id')
        
        logger.info(f"Received submission request: code_length={len(code) if code else 0}, language_id={language_id}")

        problem = get_object_or_404(Problem, pk=problem_id)

        if not code or not language_id:
            return Response({'success': False, 'error': 'Code and language are required.'}, status=status.HTTP_400_BAD_REQUEST)

        test_cases = problem.testcase_set.filter(is_sample=False).all()
        if not test_cases.exists():
            return Response({'success': False, 'error': 'This problem has no hidden test cases for evaluation.'}, status=status.HTTP_400_BAD_REQUEST)

        passed_cases = 0
        results = []
        final_status = "Accepted" # Assume success until a test case fails

        for case in test_cases:
            result = call_judge0_api(code, language_id, stdin=case.input_data, expected_output=case.expected_output)
            
            if not result['success']:
                final_status = 'System Error'
                break

            data = result['data']
            case_status_id = data.get('status', {}).get('id')
            case_status_desc = data.get('status', {}).get('description', 'Error')
            
            # Clean and compare output properly
            actual_output = data.get('stdout', '').strip() if data.get('stdout') else ''
            expected_output = case.expected_output.strip() if case.expected_output else ''
            
            # Check if output matches (considering both Judge0 status and output comparison)
            is_correct = (case_status_id == 3) and (actual_output == expected_output)
            
            results.append({
                'case_id': case.id, 
                'status': case_status_desc, 
                'is_correct': is_correct,
                'actual_output': actual_output,
                'expected_output': expected_output
            })

            if is_correct:
                passed_cases += 1
            else:
                # First failure determines the overall status
                if final_status == "Accepted":
                    if case_status_id != 3:
                        final_status = case_status_desc
                    else:
                        final_status = "Wrong Answer"
        
        score = int((passed_cases / len(test_cases)) * 100) if test_cases else 0

        # Create submission record (use admin user for testing)
        from django.contrib.auth.models import User
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        
        submission = Submission.objects.create(
            user=admin_user,
            problem=problem,
            code=code,
            language_id=language_id,
            status=final_status,
            score=score
        )

        return Response({
            'success': True,
            'submission_id': submission.id,
            'status': final_status,
            'score': score,
            'passed_cases': passed_cases,
            'total_cases': len(test_cases),
            'results': results
        })
    except Exception as e:
        logger.error(f"Error in submit_solution: {e}")
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def health_check(request):
    """
    Health check endpoint for the Judge0 API.
    """
    try:
        response = requests.get(f"{JUDGE0_API_URL}/health", timeout=10)
        response.raise_for_status()
        return Response({"success": True, "message": "Judge0 API is healthy."}, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        logger.error(f"Judge0 API health check failed: {e}")
        return Response({"success": False, "error": "Judge0 API is not reachable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)