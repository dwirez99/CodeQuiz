from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quiz.models import Quiz, Problem, TestCase

class Command(BaseCommand):
    help = 'Create admin user and sample quiz, problem, and testcase.'

    def handle(self, *args, **options):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))

        # Create Quiz
        quiz, created = Quiz.objects.get_or_create(
            title='Sample Quiz',
            defaults={
                'description': 'This is a sample quiz.',
                'time_limit': 1800
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Sample Quiz created.'))
        else:
            self.stdout.write(self.style.WARNING('Sample Quiz already exists.'))

        # Create Problem
        problem, created = Problem.objects.get_or_create(
            quiz=quiz,
            title='Print Hello World',
            defaults={
                'description': 'Write a program that prints Hello World.',
                'starter_code': 'print("")',
                'solution': 'print("Hello World")',
                'difficulty': 'easy',
                'language_id': 71
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Sample Problem created.'))
        else:
            self.stdout.write(self.style.WARNING('Sample Problem already exists.'))

        # Create TestCase
        testcase, created = TestCase.objects.get_or_create(
            problem=problem,
            input_data='',
            expected_output='Hello World',
            defaults={'is_sample': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Sample TestCase created.'))
        else:
            self.stdout.write(self.style.WARNING('Sample TestCase already exists.'))
