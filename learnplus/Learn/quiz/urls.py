from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # URLs pour les quiz
    path('cours/<int:cours_id>/quiz/', views.liste_quiz, name='liste_quiz'),
    path('quiz/<int:quiz_id>/', views.detail_quiz, name='detail_quiz'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/', views.quiz_question, name='quiz_question'),
    path('attempt/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),
    path('attempt/<int:attempt_id>/time/', views.check_time_remaining, name='check_time'),
    
    # URLs pour les devoirs
    path('cours/<int:cours_id>/assignments/', views.liste_assignments, name='liste_assignments'),
    path('assignment/<int:assignment_id>/', views.detail_assignment, name='detail_assignment'),
]
