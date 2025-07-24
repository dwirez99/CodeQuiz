from django.urls import path
from . import api_views

app_name = 'quiz_api'

urlpatterns = [
    path('run/<int:problem_id>/', api_views.run_code, name='run_code'),
    path('submit/<int:problem_id>/', api_views.submit_solution, name='submit_solution'),
]
