from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quiz.models import Quiz, Problem, TestCase

class Command(BaseCommand):
    help = 'Setup sample quiz data for testing admin interface'

    def handle(self, *args, **options):
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser "admin" created with password "admin123"'))
        else:
            self.stdout.write(self.style.WARNING('Superuser "admin" already exists'))

        # Create sample quiz
        quiz, created = Quiz.objects.get_or_create(
            title="Python Programming Quiz",
            defaults={
                'description': 'A comprehensive quiz to test Python programming skills',
                'time_limit': 3600  # 1 hour
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Quiz "{quiz.title}" created'))
        else:
            self.stdout.write(self.style.WARNING(f'Quiz "{quiz.title}" already exists'))

        # Sample Problem 1: Two Sum
        problem1, created = Problem.objects.get_or_create(
            quiz=quiz,
            title="Two Sum",
            defaults={
                'description': '''Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].''',
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
            # Add test cases for Two Sum
            TestCase.objects.create(
                problem=problem1,
                input_data='[2, 7, 11, 15]\n9',
                expected_output='[0, 1]',
                is_sample=True
            )
            TestCase.objects.create(
                problem=problem1,
                input_data='[3, 2, 4]\n6',
                expected_output='[1, 2]',
                is_sample=False
            )
            TestCase.objects.create(
                problem=problem1,
                input_data='[3, 3]\n6',
                expected_output='[0, 1]',
                is_sample=False
            )
            self.stdout.write(self.style.SUCCESS(f'Problem "{problem1.title}" created with test cases'))

        # Sample Problem 2: Palindrome Check
        problem2, created = Problem.objects.get_or_create(
            quiz=quiz,
            title="Palindrome Number",
            defaults={
                'description': '''Given an integer x, return true if x is palindrome integer.

An integer is a palindrome when it reads the same backward as forward.

Example 1:
Input: x = 121
Output: true
Explanation: 121 reads as 121 from left to right and from right to left.

Example 2:
Input: x = -121
Output: false
Explanation: From left to right, it reads -121. From right to left, it becomes 121-. Therefore it is not a palindrome.''',
                'starter_code': '''def is_palindrome(x):
    """
    Check if an integer is a palindrome.
    
    Args:
        x: Integer to check
    
    Returns:
        Boolean indicating if x is palindrome
    """
    # Your code here
    pass

# Test your solution
if __name__ == "__main__":
    test_cases = [121, -121, 10, 0, 1221]
    for test in test_cases:
        result = is_palindrome(test)
        print(f"is_palindrome({test}) = {result}")''',
                'solution': '''def is_palindrome(x):
    """
    Check if an integer is a palindrome.
    
    Args:
        x: Integer to check
    
    Returns:
        Boolean indicating if x is palindrome
    """
    if x < 0:
        return False
    
    # Convert to string and check if it reads same forwards and backwards
    s = str(x)
    return s == s[::-1]

# Test your solution
if __name__ == "__main__":
    test_cases = [121, -121, 10, 0, 1221]
    for test in test_cases:
        result = is_palindrome(test)
        print(f"is_palindrome({test}) = {result}")''',
                'difficulty': 'easy'
            }
        )

        if created:
            # Add test cases for Palindrome Number
            TestCase.objects.create(
                problem=problem2,
                input_data='121',
                expected_output='True',
                is_sample=True
            )
            TestCase.objects.create(
                problem=problem2,
                input_data='-121',
                expected_output='False',
                is_sample=True
            )
            TestCase.objects.create(
                problem=problem2,
                input_data='10',
                expected_output='False',
                is_sample=False
            )
            TestCase.objects.create(
                problem=problem2,
                input_data='0',
                expected_output='True',
                is_sample=False
            )
            self.stdout.write(self.style.SUCCESS(f'Problem "{problem2.title}" created with test cases'))

        # Sample Problem 3: FizzBuzz
        problem3, created = Problem.objects.get_or_create(
            quiz=quiz,
            title="FizzBuzz",
            defaults={
                'description': '''Given an integer n, return a string array answer (1-indexed) where:

- answer[i] == "FizzBuzz" if i is divisible by 3 and 5.
- answer[i] == "Fizz" if i is divisible by 3.
- answer[i] == "Buzz" if i is divisible by 5.
- answer[i] == i (as a string) if none of the above conditions are true.

Example:
Input: n = 3
Output: ["1","2","Fizz"]

Example:
Input: n = 5
Output: ["1","2","Fizz","4","Buzz"]''',
                'starter_code': '''def fizz_buzz(n):
    """
    Generate FizzBuzz sequence up to n.
    
    Args:
        n: Upper limit (inclusive)
    
    Returns:
        List of strings representing the FizzBuzz sequence
    """
    # Your code here
    pass

# Test your solution
if __name__ == "__main__":
    n = 15
    result = fizz_buzz(n)
    print(result)''',
                'solution': '''def fizz_buzz(n):
    """
    Generate FizzBuzz sequence up to n.
    
    Args:
        n: Upper limit (inclusive)
    
    Returns:
        List of strings representing the FizzBuzz sequence
    """
    result = []
    
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    
    return result

# Test your solution
if __name__ == "__main__":
    n = 15
    result = fizz_buzz(n)
    print(result)''',
                'difficulty': 'medium'
            }
        )

        if created:
            # Add test cases for FizzBuzz
            TestCase.objects.create(
                problem=problem3,
                input_data='3',
                expected_output='["1", "2", "Fizz"]',
                is_sample=True
            )
            TestCase.objects.create(
                problem=problem3,
                input_data='5',
                expected_output='["1", "2", "Fizz", "4", "Buzz"]',
                is_sample=True
            )
            TestCase.objects.create(
                problem=problem3,
                input_data='15',
                expected_output='["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]',
                is_sample=False
            )
            self.stdout.write(self.style.SUCCESS(f'Problem "{problem3.title}" created with test cases'))

        self.stdout.write(self.style.SUCCESS('Sample data setup completed!'))
        self.stdout.write(self.style.SUCCESS('You can now access the admin interface at http://localhost:8000/admin/'))
        self.stdout.write(self.style.SUCCESS('Login with username: admin, password: admin123'))
