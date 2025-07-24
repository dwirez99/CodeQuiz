from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quiz.models import Quiz, Problem, TestCase

class Command(BaseCommand):
    help = 'Create sample quiz data for testing admin interface'

    def handle(self, *args, **options):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))

        # Create sample quiz
        quiz, created = Quiz.objects.get_or_create(
            title='Python Programming Quiz',
            defaults={
                'description': 'A quiz to test basic Python programming skills',
                'time_limit': 3600,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created quiz: {quiz.title}'))

        # Create sample problems
        problems_data = [
            {
                'title': 'Two Sum',
                'description': '''Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].''',
                'starter_code': '''def two_sum(nums, target):
    # Write your solution here
    pass

# Test the function
nums = [2, 7, 11, 15]
target = 9
result = two_sum(nums, target)
print(result)''',
                'solution': '''def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Test the function
nums = [2, 7, 11, 15]
target = 9
result = two_sum(nums, target)
print(result)''',
                'difficulty': 'easy',
                'test_cases': [
                    {'input': '2 7 11 15\n9', 'expected': '[0, 1]', 'is_sample': True},
                    {'input': '3 2 4\n6', 'expected': '[1, 2]', 'is_sample': False},
                    {'input': '3 3\n6', 'expected': '[0, 1]', 'is_sample': False},
                ]
            },
            {
                'title': 'Palindrome Check',
                'description': '''Write a function to check if a given string is a palindrome.

A palindrome is a word, phrase, number, or other sequence of characters which reads the same backward as forward.

Example:
Input: "racecar"
Output: True

Input: "hello"
Output: False''',
                'starter_code': '''def is_palindrome(s):
    # Write your solution here
    pass

# Test the function
test_string = input().strip()
result = is_palindrome(test_string)
print(result)''',
                'solution': '''def is_palindrome(s):
    # Convert to lowercase and remove non-alphanumeric characters
    cleaned = ''.join(char.lower() for char in s if char.isalnum())
    return cleaned == cleaned[::-1]

# Test the function
test_string = input().strip()
result = is_palindrome(test_string)
print(result)''',
                'difficulty': 'easy',
                'test_cases': [
                    {'input': 'racecar', 'expected': 'True', 'is_sample': True},
                    {'input': 'hello', 'expected': 'False', 'is_sample': True},
                    {'input': 'A man a plan a canal Panama', 'expected': 'True', 'is_sample': False},
                    {'input': 'race a car', 'expected': 'False', 'is_sample': False},
                ]
            },
            {
                'title': 'Fibonacci Sequence',
                'description': '''Write a function to generate the nth Fibonacci number.

The Fibonacci sequence is defined as:
F(0) = 0, F(1) = 1
F(n) = F(n-1) + F(n-2) for n > 1

Example:
Input: 10
Output: 55''',
                'starter_code': '''def fibonacci(n):
    # Write your solution here
    pass

# Test the function
n = int(input())
result = fibonacci(n)
print(result)''',
                'solution': '''def fibonacci(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Test the function
n = int(input())
result = fibonacci(n)
print(result)''',
                'difficulty': 'medium',
                'test_cases': [
                    {'input': '0', 'expected': '0', 'is_sample': True},
                    {'input': '1', 'expected': '1', 'is_sample': True},
                    {'input': '10', 'expected': '55', 'is_sample': True},
                    {'input': '20', 'expected': '6765', 'is_sample': False},
                ]
            }
        ]

        for problem_data in problems_data:
            test_cases = problem_data.pop('test_cases')
            problem, created = Problem.objects.get_or_create(
                quiz=quiz,
                title=problem_data['title'],
                defaults=problem_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created problem: {problem.title}'))
                
                # Create test cases
                for tc_data in test_cases:
                    TestCase.objects.create(
                        problem=problem,
                        **tc_data
                    )
                self.stdout.write(self.style.SUCCESS(f'Created {len(test_cases)} test cases for {problem.title}'))

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(self.style.WARNING('You can now login to admin with: admin/admin123'))
