from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    time_limit = models.IntegerField(default=3600)

    def __str__(self):
        return self.title

class Problem(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='problems', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    starter_code = models.TextField(blank=True)
    solution = models.TextField()
    difficulty = models.CharField(max_length=50, choices=[
        ('easy', 'Easy'),('medium', 'Medium'),('hard', 'Hard'),
    ])
    LANGUAGE_CHOICES = [
        (71, 'Python 3'),
        (54, 'C++ (GCC 9.2.0)'),
        (62, 'Java (OpenJDK 13.0.1)'),
        (63, 'JavaScript (Node.js 12.14.0)'),
        (50, 'C (GCC 9.2.0)'),
        (68, 'PHP (7.4.1)'),
        (70, 'Python 2'),
        (72, 'Ruby 2.7.0'),
        (60, 'Go (1.13.5)'),
        (73, 'Rust 1.40.0'),
        (52, 'C# (Mono 6.6.0.161)'),
        (61, 'Kotlin (1.3.70)'),
        (78, 'Kotlin (JVM 1.6.10)'),
        (80, 'TypeScript (3.7.4)'),
        (74, 'Swift (5.2.3)'),
        (79, 'Scala (2.13.4)'),
        (69, 'Perl (5.28.1)'),
        (65, 'R (4.0.0)'),
        (67, 'Pascal (FPC 3.0.4)'),
        (64, 'Lua (5.3.5)'),
        (75, 'Haskell (GHC 8.8.1)'),
        (76, 'Objective-C (Clang 7.0.1)'),
        (77, 'Groovy (3.0.3)'),
        (49, 'C (GCC 8.3.0)'),
        (55, 'C++ (GCC 8.3.0)'),
        (56, 'C++ (GCC 7.4.0)'),
        (57, 'C++ (GCC 6.3.0)'),
        (58, 'C++ (GCC 5.4.0)'),
        (59, 'C++ (GCC 4.9.2)'),
    ]
    language_id = models.IntegerField(choices=LANGUAGE_CHOICES, default=71, help_text="Programming language for this problem.")

    def __str__(self):
        return self.title

class TestCase(models.Model):
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)

    def __str__(self):
        return f"Test Case for {self.problem.title}"

class Submission(models.Model):
    STATUS_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Partially Accepted', 'Partially Accepted'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Compilation Error', 'Compilation Error'),
        ('Runtime Error', 'Runtime Error'),
        ('Time Limit Exceeded', 'Time Limit Exceeded'),
        ('Memory Limit Exceeded', 'Memory Limit Exceeded'),
        ('In Queue', 'In Queue'),
        ('Processing', 'Processing'),
        ('Internal Error', 'Internal Error'),
        ('Exec Format Error', 'Exec Format Error'),
        ('Unknown', 'Unknown'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language_id = models.IntegerField(default=71)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='In Queue')
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    output = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    execution_time = models.FloatField(blank=True, null=True)
    memory = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Submission by {self.user.username} for {self.problem.title}"