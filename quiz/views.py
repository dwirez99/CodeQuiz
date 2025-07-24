from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
import json
from .models import Quiz, Problem, Submission, TestCase
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        problems = quiz.problems.all().order_by('id')
        context = {
            'quiz': quiz,
            'problems': problems,
            'problem_count': problems.count(),
            'total_time': quiz.time_limit,
            'time_hours': quiz.time_limit // 3600,
            'time_minutes': (quiz.time_limit % 3600) // 60,
        }
        logger.debug(f"Quiz Detail Context: {context}")
        return render(request, 'quiz/quiz_detail.html', context)
    except Exception as e:
        return render(request, 'quiz/quiz_detail.html', {
            'quiz': None,
            'problems': [],
            'problem_count': 0,
            'total_time': 0,
            'time_hours': 0,
            'time_minutes': 0,
            'error_message': str(e),
        })

def submission_list(request):
    submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'quiz/submission_list.html', {'submissions': submissions})

def code_editor(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    quiz = problem.quiz
    all_problems = quiz.problems.all().order_by('id')
    current_index = list(all_problems).index(problem)
    
    # Get sample test cases
    sample_test_cases = problem.testcase_set.filter(is_sample=True)
    
    context = {
        'problem': problem,
        'quiz': quiz,
        'all_problems': all_problems,
        'current_index': current_index,
        'total_problems': all_problems.count(),
        'sample_test_cases': sample_test_cases,
        'next_problem': all_problems[current_index + 1] if current_index + 1 < len(all_problems) else None,
        'prev_problem': all_problems[current_index - 1] if current_index > 0 else None,
    }
    return render(request, 'quiz/code_editor.html', context)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    code = request.data.get('code')
    language_id = request.data.get('language_id', 71)
    input_data = request.data.get('input', '')

    # Submit to Judge0 for execution
    judge0_response = submit_to_judge0(code, language_id, input_data)

    # Create a submission record
    submission_user = request.user if request.user.is_authenticated else None
    
    submission = Submission.objects.create(
        user=submission_user,
        problem=problem,
        code=code,
        language_id=language_id,
        status=judge0_response.get('status', {}).get('description', 'In Queue'),
        output=judge0_response.get('stdout'),
        error=judge0_response.get('stderr'),
        execution_time=judge0_response.get('time'),
        memory=judge0_response.get('memory'),
    )

    return Response({
        'success': True,
        'submission_id': submission.id,
        'status': judge0_response.get('status', {}).get('description', 'In Queue'),
        'output': judge0_response.get('stdout'),
        'error': judge0_response.get('stderr'),
        'execution_time': judge0_response.get('time'),
        'memory': judge0_response.get('memory'),
    })

@api_view(['GET'])
def check_submission(request, submission_id):
    """Check the status of a submission"""
    submission = get_object_or_404(Submission, id=submission_id)
    
    return Response({
        'submission_id': submission.id,
        'status': submission.status,
        'code': submission.code,
        'problem_id': submission.problem.id,
        'submitted_at': submission.submitted_at,
    })

def submit_to_judge0(code, language_id, input_data):
    """Helper function to submit code to Judge0."""
    judge0_url = getattr(settings, 'JUDGE0_URL', 'http://localhost:2358')
    
    post_data = {
        "source_code": code,
        "language_id": language_id,
        "stdin": input_data,
    }

    try:
        response = requests.post(f"{judge0_url}/submissions?base64_encoded=false&wait=true", json=post_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'status': {'description': 'API Error'}, 'stderr': str(e)}

def normalize_output(output):
    """Normalize output by removing extra whitespace and newlines."""
    if not output:
        return ""
    # Remove trailing whitespace and normalize line endings
    return re.sub(r'\s+$', '', output.strip()).replace('\r\n', '\n').replace('\r', '\n')

def compare_outputs(expected, actual):
    """Compare expected and actual outputs with normalization."""
    expected_normalized = normalize_output(expected)
    actual_normalized = normalize_output(actual)
    return expected_normalized == actual_normalized

@api_view(['POST'])
@permission_classes([AllowAny])
def evaluate_solution(request, problem_id):
    """Evaluate solution against all test cases for final submission."""
    problem = get_object_or_404(Problem, id=problem_id)
    code = request.data.get('code')
    language_id = request.data.get('language_id', 71)

    if not code or not code.strip():
        return Response({
            'success': False,
            'error': 'Code cannot be empty'
        })

    # Get all test cases for this problem
    test_cases = TestCase.objects.filter(problem=problem)
    
    if not test_cases.exists():
        return Response({
            'success': False,
            'error': 'No test cases found for this problem'
        })

    total_tests = test_cases.count()
    passed_tests = 0
    test_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        # Execute code with test case input
        judge0_response = submit_to_judge0(code, language_id, test_case.input_data)
        
        # Check if execution was successful
        status = judge0_response.get('status', {}).get('description', 'Unknown')
        actual_output = judge0_response.get('stdout', '')
        error_output = judge0_response.get('stderr', '')
        
        # Check if output matches expected
        is_correct = False
        if status == 'Accepted' and not error_output:
            is_correct = compare_outputs(test_case.expected_output, actual_output)
            if is_correct:
                passed_tests += 1
        
        test_results.append({
            'test_number': i,
            'input': test_case.input_data if test_case.is_sample else 'Hidden',
            'expected': test_case.expected_output if test_case.is_sample else 'Hidden',
            'actual': actual_output,
            'error': error_output,
            'status': status,
            'passed': is_correct,
            'is_sample': test_case.is_sample,
            'execution_time': judge0_response.get('time'),
            'memory': judge0_response.get('memory'),
        })

    # Calculate score
    score = int((passed_tests / total_tests) * 100)
    
    # Determine overall status
    if passed_tests == total_tests:
        overall_status = 'Accepted'
    elif passed_tests > 0:
        overall_status = 'Partially Accepted'
    else:
        overall_status = 'Wrong Answer'

    # Create submission record
    submission_user = request.user if request.user.is_authenticated else None
    
    submission = Submission.objects.create(
        user=submission_user,
        problem=problem,
        code=code,
        language_id=language_id,
        status=overall_status,
        score=score,
        output=f"Passed {passed_tests}/{total_tests} test cases",
        execution_time=sum([r.get('execution_time', 0) or 0 for r in test_results]),
        memory=max([r.get('memory', 0) or 0 for r in test_results]),
    )

    return Response({
        'success': True,
        'submission_id': submission.id,
        'status': overall_status,
        'score': score,
        'passed_tests': passed_tests,
        'total_tests': total_tests,
        'test_results': test_results,
        'message': f"Solution {'accepted' if overall_status == 'Accepted' else 'needs improvement'}! Passed {passed_tests}/{total_tests} test cases."
    })

# Create your views here.
