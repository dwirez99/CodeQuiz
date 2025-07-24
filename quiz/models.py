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