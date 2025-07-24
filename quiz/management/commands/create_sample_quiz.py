from django.core.management.base import BaseCommand
from quiz.models import Quiz, Problem, TestCase
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create sample quiz with problems and test cases'

    def handle(self, *args, **options):
        # Create a sample quiz
        quiz, created = Quiz.objects.get_or_create(
            title="Python Basics Challenge",
            defaults={
                'description': """This quiz tests your understanding of Python fundamentals including:
- Variables and data types
- Control structures (if/else, loops)
- Functions
- Basic algorithms

Time limit: 60 minutes
Good luck!""",
                'time_limit': 3600
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created quiz: {quiz.title}'))
        else:
            self.stdout.write(f'Quiz already exists: {quiz.title}')

        # Create Problem 1: Two Sum
        problem1, created = Problem.objects.get_or_create(
            quiz=quiz,
            title="Two Sum",
            defaults={
                'description': """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Constraints:
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- Only one valid answer exists.""",
                'starter_code': '''def two_sum(nums, target):
    """
    Find two numbers in the array that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
    
    Returns:
        List of two indices
    """
    # Your code here
    pass

# Test your solution
if __name__ == "__main__":
    nums = [2, 7, 11, 15]
    target = 9
    result = two_sum(nums, target)
    print(result)''',
                'solution': '''def two_sum(nums, target):
    """
    Find two numbers in the array that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
    
    Returns:
        List of two indices
    """
    num_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []

# Test your solution
if __name__ == "__main__":
    nums = [2, 7, 11, 15]
    target = 9
    result = two_sum(nums, target)
    print(result)''',
                'difficulty': 'easy'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created problem: {problem1.title}'))
            
            # Create test cases for Problem 1
            TestCase.objects.create(
                problem=problem1,
                input_data="[2, 7, 11, 15]\n9",
                expected_output="[0, 1]",
                is_sample=True
            )
            TestCase.objects.create(
                problem=problem1,
                input_data="[3, 2, 4]\n6",
                expected_output="[1, 2]",
                is_sample=False
            )
            TestCase.objects.create(
                problem=problem1,
                input_data="[3, 3]\n6",
                expected_output="[0, 1]",
                is_sample=False
            )

        # Create Problem 2: Palindrome Check
        problem2, created = Problem.objects.get_or_create(
            quiz=quiz,
            title="Palindrome Check",
            defaults={
                'description': """Write a function that checks if a given string is a palindrome (reads the same forwards and backwards).

The function should ignore case, spaces, and punctuation.

Examples:
Input: "A man a plan a canal Panama"
Output: True

Input: "race a car"
Output: False

Input: "hello"
Output: False""",
                'starter_code': '''def is_palindrome(s):
    """
    Check if string is a palindrome.
    
    Args:
        s: Input string
    
    Returns:
        Boolean indicating if string is palindrome
    """
    # Your code here
    pass

# Test your solution
if __name__ == "__main__":
    test_cases = [
        "A man a plan a canal Panama",
        "race a car",
        "hello"
    ]
    for test in test_cases:
        result = is_palindrome(test)
        print(f"'{test}' -> {result}")''',
                'solution': '''def is_palindrome(s):
    """
    Check if string is a palindrome.
    
    Args:
        s: Input string
    
    Returns:
        Boolean indicating if string is palindrome
    """
    # Clean the string: keep only alphanumeric, convert to lowercase
    cleaned = ''.join(char.lower() for char in s if char.isalnum())
    
    # Check if cleaned string equals its reverse
    return cleaned == cleaned[::-1]

# Test your solution
if __name__ == "__main__":
    test_cases = [
        "A man a plan a canal Panama",
        "race a car", 
        "hello"
    ]
    for test in test_cases:
        result = is_palindrome(test)
        print(f"'{test}' -> {result}")''',
                'difficulty': 'easy'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created problem: {problem2.title}'))
            
            # Create test cases for Problem 2
            TestCase.objects.create(
                problem=problem2,
                input_data="A man a plan a canal Panama",
                expected_output="True",
                is_sample=True
            )
            TestCase.objects.create(
                problem=problem2,
                input_data="race a car",
                expected_output="False",
                is_sample=False
            )
            TestCase.objects.create(
                problem=problem2,
                input_data="hello",
                expected_output="False",
                is_sample=False
            )

        self.stdout.write(self.style.SUCCESS('Sample quiz creation completed!'))
        self.stdout.write(f'Quiz: {quiz.title}')
        self.stdout.write(f'Problems: {quiz.problems.count()}')
        for problem in quiz.problems.all():
            self.stdout.write(f'  - {problem.title}: {problem.testcase_set.count()} test cases')
