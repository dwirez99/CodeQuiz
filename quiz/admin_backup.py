from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea
from django.utils.safestring import mark_safe
from django.urls import reverse, path
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json
import requests
from .models import Quiz, Problem, TestCase, Submission

class CodeEditorWidget(Textarea):
    """Custom widget for code editor in admin"""
    
    def __init__(self, attrs=None, mode='python'):
        self.mode = mode
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs['class'] = attrs.get('class', '') + ' code-editor'
        attrs['data-mode'] = self.mode
        return super().render(name, value, attrs, renderer)
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js',
            'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/mode-python.js',
            'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/mode-java.js',
            'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/mode-c_cpp.js',
            'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/theme-monokai.js',
        )

class ProblemAdminForm(ModelForm):
    """Custom form for Problem model with code editor"""
    
    starter_code = CharField(
        widget=CodeEditorWidget(attrs={'rows': 15, 'cols': 80}),
        required=False,
        help_text="Initial code template for students"
    )
    
    solution = CharField(
        widget=CodeEditorWidget(attrs={'rows': 15, 'cols': 80}),
        help_text="Complete solution code for testing"
    )
    
    class Meta:
        model = Problem
        fields = '__all__'

class TestCaseInline(admin.TabularInline):
    """Inline admin for test cases"""
    model = TestCase
    extra = 1
    fields = ('input_data', 'expected_output', 'is_sample')
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['input_data'].widget = Textarea(attrs={'rows': 3, 'cols': 40})
        formset.form.base_fields['expected_output'].widget = Textarea(attrs={'rows': 3, 'cols': 40})
        return formset

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    form = ProblemAdminForm
    inlines = [TestCaseInline]
    list_display = ('title', 'quiz', 'difficulty', 'test_solution_link')
    list_filter = ('quiz', 'difficulty')
    search_fields = ('title', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('quiz', 'title', 'description', 'difficulty')
        }),
        ('Code', {
            'fields': ('starter_code', 'solution'),
            'classes': ('wide',)
        }),
    )
    
    def test_solution_link(self, obj):
        """Add a link to test the solution"""
        if obj.pk:
            url = reverse('admin:test_solution', args=[obj.pk])
            return mark_safe(f'<a href="{url}" target="_blank" class="button">Test Solution</a>')
        return '-'
    test_solution_link.short_description = 'Test Solution'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'test-solution/<int:problem_id>/',
                self.admin_site.admin_view(self.test_solution_view),
                name='test_solution',
            ),
            path(
                'execute-code/',
                self.admin_site.admin_view(self.execute_code_view),
                name='execute_code',
            ),
        ]
        return custom_urls + urls
    
    def test_solution_view(self, request, problem_id):
        """View for testing problem solution with code editor"""
        problem = get_object_or_404(Problem, pk=problem_id)
        
        context = {
            'problem': problem,
            'title': f'Test Solution: {problem.title}',
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        
        return render(request, 'admin/quiz/problem/test_solution.html', context)
    
    def execute_code_view(self, request):
        """AJAX view to execute code using Judge0"""
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                code = data.get('code')
                language_id = data.get('language_id', 71)  # Default to Python
                input_data = data.get('input', '')
                
                # Submit to Judge0
                submission_data = {
                    'source_code': code,
                    'language_id': language_id,
                    'stdin': input_data
                }
                
                # Replace with your Judge0 API endpoint
                judge0_url = getattr(settings, 'JUDGE0_URL', 'http://localhost:2358')
                
                response = requests.post(
                    f'{judge0_url}/submissions?wait=true',
                    json=submission_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 201:
                    result = response.json()
                    return JsonResponse({
                        'success': True,
                        'output': result.get('stdout', ''),
                        'error': result.get('stderr', ''),
                        'status': result.get('status', {}).get('description', 'Unknown'),
                        'execution_time': result.get('time', ''),
                        'memory': result.get('memory', '')
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to execute code'
                    })
                    
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    class Media:
        css = {
            'all': ('admin/css/code_editor_admin.css',)
        }
        js = ('admin/js/code_editor_admin.js',)

class ProblemInline(admin.TabularInline):
    """Inline admin for problems in quiz"""
    model = Problem
    extra = 1
    fields = ('title', 'difficulty', 'description_preview', 'test_case_count')
    readonly_fields = ('description_preview', 'test_case_count')
    show_change_link = True
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return '-'
    description_preview.short_description = 'Description Preview'
    
    def test_case_count(self, obj):
        if obj.pk:
            count = obj.testcase_set.count()
            return f'{count} test cases'
        return '-'
    test_case_count.short_description = 'Test Cases'

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [ProblemInline]
    list_display = ('title', 'created_at', 'time_limit_display', 'problem_count', 'is_active', 'quiz_actions')
    list_filter = ('created_at', 'time_limit')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    list_editable = ('time_limit',)
    actions = ['duplicate_quiz', 'activate_quiz', 'deactivate_quiz']
    
    fieldsets = (
        ('Quiz Information', {
            'fields': ('title', 'description'),
            'description': 'Basic information about the quiz'
        }),
        ('Quiz Settings', {
            'fields': ('time_limit',),
            'description': 'Configure quiz timing and behavior'
        }),
    )
    
    def problem_count(self, obj):
        count = obj.problems.count()
        if count == 0:
            return mark_safe(f'<span style="color: red;">{count} problems</span>')
        return mark_safe(f'<span style="color: green;">{count} problems</span>')
    problem_count.short_description = 'Problems'
    
    def time_limit_display(self, obj):
        hours = obj.time_limit // 3600
        minutes = (obj.time_limit % 3600) // 60
        if hours > 0:
            return f'{hours}h {minutes}m'
        return f'{minutes}m'
    time_limit_display.short_description = 'Time Limit'
    
    def is_active(self, obj):
        # A quiz is considered active if it has problems
        return obj.problems.exists()
    is_active.boolean = True
    is_active.short_description = 'Active'
    
    def quiz_actions(self, obj):
        actions = []
        if obj.pk:
            # View quiz link
            actions.append(f'<a href="/quiz/{obj.pk}/" target="_blank" class="button">View Quiz</a>')
            # Duplicate quiz link
            actions.append(f'<a href="?action=duplicate&ids={obj.pk}" class="button">Duplicate</a>')
        return mark_safe(' '.join(actions))
    quiz_actions.short_description = 'Actions'
    
    def duplicate_quiz(self, request, queryset):
        """Action to duplicate selected quizzes"""
        for quiz in queryset:
            # Create a new quiz with copied data
            new_quiz = Quiz.objects.create(
                title=f"{quiz.title} (Copy)",
                description=quiz.description,
                time_limit=quiz.time_limit
            )
            # Copy all problems and their test cases
            for problem in quiz.problems.all():
                new_problem = Problem.objects.create(
                    quiz=new_quiz,
                    title=problem.title,
                    description=problem.description,
                    starter_code=problem.starter_code,
                    solution=problem.solution,
                    difficulty=problem.difficulty
                )
                # Copy test cases
                for test_case in problem.testcase_set.all():
                    TestCase.objects.create(
                        problem=new_problem,
                        input_data=test_case.input_data,
                        expected_output=test_case.expected_output,
                        is_sample=test_case.is_sample
                    )
        self.message_user(request, f"Successfully duplicated {queryset.count()} quiz(es).")
    duplicate_quiz.short_description = "Duplicate selected quizzes"
    
    def activate_quiz(self, request, queryset):
        """Action to activate quizzes (placeholder for future functionality)"""
        self.message_user(request, f"Activated {queryset.count()} quiz(es).")
    activate_quiz.short_description = "Activate selected quizzes"
    
    def deactivate_quiz(self, request, queryset):
        """Action to deactivate quizzes (placeholder for future functionality)"""
        self.message_user(request, f"Deactivated {queryset.count()} quiz(es).")
    deactivate_quiz.short_description = "Deactivate selected quizzes"

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample', 'input_preview', 'output_preview')
    list_filter = ('is_sample', 'problem__quiz')
    search_fields = ('problem__title',)
    
    fieldsets = (
        ('Test Case Information', {
            'fields': ('problem', 'is_sample')
        }),
        ('Test Data', {
            'fields': ('input_data', 'expected_output'),
            'classes': ('wide',)
        }),
    )
    
    def input_preview(self, obj):
        return obj.input_data[:50] + '...' if len(obj.input_data) > 50 else obj.input_data
    input_preview.short_description = 'Input Preview'
    
    def output_preview(self, obj):
        return obj.expected_output[:50] + '...' if len(obj.expected_output) > 50 else obj.expected_output
    output_preview.short_description = 'Expected Output Preview'

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status', 'score', 'submitted_at', 'view_code_link')
    list_filter = ('status', 'problem__quiz', 'submitted_at')
    search_fields = ('user__username', 'problem__title')
    readonly_fields = ('user', 'problem', 'code', 'submitted_at')
    date_hierarchy = 'submitted_at'
    
    def view_code_link(self, obj):
        if obj.pk:
            url = reverse('admin:view_submission_code', args=[obj.pk])
            return mark_safe(f'<a href="{url}" target="_blank" class="button">View Code</a>')
        return '-'
    view_code_link.short_description = 'View Code'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'view-code/<int:submission_id>/',
                self.admin_site.admin_view(self.view_submission_code),
                name='view_submission_code',
            ),
        ]
        return custom_urls + urls
    
    def view_submission_code(self, request, submission_id):
        """View for displaying submission code"""
        submission = get_object_or_404(Submission, pk=submission_id)
        
        context = {
            'submission': submission,
            'title': f'Submission Code: {submission.problem.title}',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/quiz/submission/view_code.html', context)
