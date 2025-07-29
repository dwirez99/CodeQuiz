from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Quiz, Problem, TestCase, Submission

# Basic admin classes
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'time_limit')
    search_fields = ('title', 'description')

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz', 'difficulty', 'get_language')
    list_filter = ('quiz', 'difficulty', 'language_id')
    fields = ('title', 'quiz', 'difficulty', 'language_id', 'description', 'starter_code', 'solution')

    def get_language(self, obj):
        return dict(obj.LANGUAGE_CHOICES).get(obj.language_id, obj.language_id)
    get_language.short_description = 'Language'

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample')
    list_filter = ('is_sample',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status_badge', 'score', 'submitted_at')
    list_filter = ('status', 'submitted_at', 'problem__quiz')
    readonly_fields = ('submitted_at',)
    search_fields = ('user__username', 'problem__title')
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('user', 'problem')
        }),
        ('Code', {
            'fields': ('code', 'language_id'),
            'classes': ('wide',)
        }),
        ('Results', {
            'fields': ('status', 'score'),
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        color_map = {
            'Accepted': 'green',
            'Partially Accepted': 'orange', 
            'Wrong Answer': 'red',
            'Compilation Error': 'purple',
            'Runtime Error': 'red',
            'Time Limit Exceeded': 'orange',
            'Memory Limit Exceeded': 'orange',
            'In Queue': 'blue',
            'Processing': 'blue',
            'Internal Error': 'gray',
            'Exec Format Error': 'gray',
            'Unknown': 'gray',
        }
        color = color_map.get(obj.status, 'gray')
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{obj.status}</span>')
    status_badge.short_description = 'Status'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make sure required fields are properly handled
        if 'problem' in form.base_fields:
            form.base_fields['problem'].required = True
            form.base_fields['problem'].empty_label = "Select a problem..."
        if 'user' in form.base_fields:
            form.base_fields['user'].required = True
            form.base_fields['user'].empty_label = "Select a user..."
        return form
