from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from quiz.models import Quiz, Question, Answer, QuizAttempt, StudentResponse
from student.models import Student
from school.models import Cours, Chapitre, Matiere

class QuizEvaluationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Créer un étudiant
        self.student_user = User.objects.create_user(
            username='student_test',
            password='test12345'
        )
        self.student = Student.objects.create(
            user=self.student_user
        )
        
        # Créer un cours et un quiz
        self.matiere = Matiere.objects.create(nom='Test Matiere')
        self.chapitre = Chapitre.objects.create(
            matiere=self.matiere,
            titre='Test Chapitre'
        )
        self.cours = Cours.objects.create(
            chapitre=self.chapitre,
            titre='Test Cours'
        )
        self.quiz = Quiz.objects.create(
            cours=self.cours,
            titre='Test Quiz',
            duree=30
        )

    def test_quiz_creation(self):
        """Test la création d'un quiz avec questions et réponses"""
        question = Question.objects.create(
            quiz=self.quiz,
            texte='Test Question?',
            points=10
        )
        Answer.objects.create(
            question=question,
            texte='Bonne réponse',
            is_correct=True
        )
        Answer.objects.create(
            question=question,
            texte='Mauvaise réponse',
            is_correct=False
        )
        
        self.assertEqual(self.quiz.questions.count(), 1)
        self.assertEqual(question.answers.count(), 2)

    def test_quiz_submission(self):
        """Test la soumission d'un quiz par un étudiant"""
        # Créer un quiz avec une question
        question = Question.objects.create(
            quiz=self.quiz,
            texte='Test Question?',
            points=10
        )
        bonne_reponse = Answer.objects.create(
            question=question,
            texte='Bonne réponse',
            is_correct=True
        )
        
        # Créer une tentative
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            student=self.student_user
        )
        
        # Soumettre une réponse
        self.client.login(username='student_test', password='test12345')
        response = StudentResponse.objects.create(
            attempt=attempt,
            question=question
        )
        response.selected_answers.add(bonne_reponse)
        response.check_correctness()
        
        self.assertTrue(response.is_correct)
        attempt.calculate_score()
        self.assertEqual(attempt.score, 10.0)

    def test_quiz_time_limit(self):
        """Test la limite de temps du quiz"""
        self.client.login(username='student_test', password='test12345')
        
        # Commencer le quiz
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            student=self.student_user
        )
        
        # Vérifier que la tentative est créée
        self.assertIsNotNone(attempt.started_at)
        self.assertIsNone(attempt.completed_at)
