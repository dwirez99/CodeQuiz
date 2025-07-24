from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('problem/<int:problem_id>/', views.code_editor, name='code_editor'),
    path('submissions/', views.submission_list, name='submission_list'),
]
