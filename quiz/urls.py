from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # Template-rendering views
    path('', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('problem/<int:problem_id>/', views.code_editor, name='code_editor'),
    path('submissions/', views.submission_list, name='submission_list'),

    # API endpoints are now also in views.py
    path('api/run/<int:problem_id>/', views.run_code, name='run_code'),
    path('api/submit/<int:problem_id>/', views.submit_solution, name='submit_solution'),
]
