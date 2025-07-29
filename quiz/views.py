import os
import requests
import logging
import json
import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, Problem, Submission, TestCase

# --- Configuration ---
logger = logging.getLogger(__name__)
JUDGE0_URL = getattr(settings, 'JUDGE0_URL', 'http://judge0:2358')

# --- Helper Functions ---

def call_judge0_api(code, language_id, stdin=None):
    """
    A single, robust helper function to submit code to the Judge0 API.
    """
    api_url = f"{JUDGE0_URL}/submissions?base64_encoded=false&wait=true"
    payload = {
        "source_code": code,
        "language_id": int(language_id),
        "stdin": stdin or "",
    }
    headers = {"Content-Type": "application/json"}

    try:
        logger.info(f"Sending request to Judge0: {api_url} with language_id: {language_id}")
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()  # Raises an exception for 4xx/5xx errors
        return {"success": True, "data": response.json()}
    except requests.exceptions.Timeout:
        logger.error("Judge0 API request timed out.")
        return {"success": False, "error": "Code execution timed out."}
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Judge0 API. Check if the service is running and accessible.")
        return {"success": False, "error": "Could not connect to the code execution service."}
    except requests.exceptions.RequestException as e:
        # This will catch the 500 error from Judge0
        logger.error(f"Judge0 API request failed: {e}")
        error_details = f"The code execution service returned an error: {e.response.status_code}"
        try:
            # Try to get more specific error from Judge0's response
            judge0_error = e.response.json()
            if 'error' in judge0_error:
                 error_details = judge0_error['error']
        except (ValueError, AttributeError):
            pass # Keep the generic error if response is not JSON
        return {"success": False, "error": error_details}
    except Exception as e:
        logger.error(f"An unexpected error occurred while calling Judge0: {e}")
        return {"success": False, "error": "An unexpected internal error occurred."}

def normalize_output(output):
    """Normalize output by removing extra whitespace and newlines."""
    if not output:
        return ""
    return re.sub(r'\s+$', '', output.strip()).replace('\r\n', '\n')

def compare_outputs(expected, actual):
    """Compare expected and actual outputs with normalization."""
    return normalize_output(expected) == normalize_output(actual)


# --- Template-Rendering Views ---

def quiz_list(request):
    """Displays a list of all available quizzes."""
    quizzes = Quiz.objects.all()
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    """Displays the details and problems for a single quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    problems = quiz.problems.all().order_by('id')
    context = {
        'quiz': quiz,
        'problems': problems,
    }
    return render(request, 'quiz/quiz_detail.html', context)

def code_editor(request, problem_id):
    """The main code editor interface for a specific problem."""
    problem = get_object_or_404(Problem, id=problem_id)
    quiz = problem.quiz
    all_problems = quiz.problems.all().order_by('id')
    current_index = list(all_problems).index(problem)
    sample_test_cases = problem.testcase_set.filter(is_sample=True)
    
    context = {
        'problem': problem,
        'quiz': quiz,
        'all_problems': all_problems,
        'supported_languages': Problem.LANGUAGE_CHOICES,
        'current_index': current_index,
        'total_problems': all_problems.count(),
        'sample_test_cases': sample_test_cases,
        'next_problem': all_problems[current_index + 1] if current_index + 1 < len(all_problems) else None,
        'prev_problem': all_problems[current_index - 1] if current_index > 0 else None,
    }
    return render(request, 'quiz/code_editor.html', context)

def submission_list(request):
    """Displays a list of the current user's past submissions."""
    if not request.user.is_authenticated:
        return render(request, 'quiz/submission_list.html', {'submissions': []})
    submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'quiz/submission_list.html', {'submissions': submissions})


# --- API Views ---

@api_view(['POST'])
@permission_classes([AllowAny]) # Use IsAuthenticated in production
def run_code(request, problem_id):
    """
    API endpoint to run code with custom input. Does not create a submission.
    This is used for the "Run" button in the editor.
    """
    code = request.data.get('code')
    language_id = request.data.get('language_id')
    custom_input = request.data.get('input', '')

    if not all([code, language_id]):
        return Response({'success': False, 'error': 'Code and language are required.'}, status=status.HTTP_400_BAD_REQUEST)

    result = call_judge0_api(code, language_id, stdin=custom_input)

    if not result.get('success'):
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    data = result['data']
    status_info = data.get('status', {})
    
    return Response({
        'success': True,
        'output': data.get('stdout') or '',
        'error': data.get('stderr') or data.get('compile_output') or '',
        'status': status_info.get('description', 'Unknown'),
        'execution_time': data.get('time', 0),
        'memory': data.get('memory', 0),
    })


@api_view(['POST'])
@permission_classes([AllowAny]) # Use IsAuthenticated in production
def submit_solution(request, problem_id):
    """
    API endpoint to submit a solution for final evaluation against all test cases.
    This is used for the "Submit" button.
    """
    problem = get_object_or_404(Problem, id=problem_id)
    code = request.data.get('code')
    language_id = request.data.get('language_id')

    if not all([code, language_id]):
        return Response({'success': False, 'error': 'Code and language are required.'}, status=status.HTTP_400_BAD_REQUEST)

    test_cases = TestCase.objects.filter(problem=problem)
    if not test_cases.exists():
        return Response({'success': False, 'error': 'No test cases found for this problem.'}, status=status.HTTP_400_BAD_REQUEST)

    passed_tests = 0
    test_results = []
    final_status = 'Accepted' # Assume success until a test fails

    for case in test_cases:
        result = call_judge0_api(code, language_id, case.input_data)
        
        if not result.get('success'):
            # If the API call itself fails, it's an internal error.
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = result['data']
        status_desc = data.get('status', {}).get('description', 'Unknown')
        is_correct = False

        if status_desc == 'Accepted':
            if compare_outputs(case.expected_output, data.get('stdout', '')):
                is_correct = True
                passed_tests += 1
            else:
                if final_status == 'Accepted': final_status = 'Wrong Answer'
        else:
            if final_status == 'Accepted': final_status = status_desc
        
        test_results.append({
            'passed': is_correct,
            'status': status_desc,
            'is_sample': case.is_sample,
        })
    
    score = int((passed_tests / test_cases.count()) * 100)
    
    # Create the submission record
    submission_user = request.user if request.user.is_authenticated else None
    if submission_user:
        Submission.objects.create(
            user=submission_user,
            problem=problem,
            code=code,
            language_id=language_id,
            status=final_status,
            score=score,
            output=f"Passed {passed_tests}/{test_cases.count()} test cases.",
        )

    return Response({
        'success': True,
        'status': final_status,
        'score': score,
        'passed_tests': passed_tests,
        'total_tests': test_cases.count(),
        'test_results': test_results,
    })
