from django.contrib import admin
from .models import Quiz, Problem, TestCase, Submission

# Simple admin registration
admin.site.register(Quiz)
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)

print("Admin models registered successfully")
