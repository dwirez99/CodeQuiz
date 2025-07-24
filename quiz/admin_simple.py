from django.contrib import admin
from .models import Quiz, Problem, TestCase, Submission

# Basic admin classes
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'time_limit')
    search_fields = ('title', 'description')

@admin.register(Problem)  
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz', 'difficulty')
    list_filter = ('quiz', 'difficulty')

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample')
    list_filter = ('is_sample',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    readonly_fields = ('user', 'problem', 'code', 'submitted_at')
