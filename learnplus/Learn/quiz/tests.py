from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Quiz, Question, Answer, QuizAttempt, StudentResponse, Assignment, AssignmentSubmission
from school.models import Cours, Chapitre, Matiere, Classe, Niveau
from .forms import QuizForm, StudentResponseForm, AssignmentSubmissionForm

class QuizModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Création des objets nécessaires pour le cours
        self.niveau = Niveau.objects.create(nom='Test Niveau')
        self.classe = Classe.objects.create(niveau=self.niveau, numeroClasse=1)
        self.matiere = Matiere.objects.create(nom='Test Matiere')
        self.chapitre = Chapitre.objects.create(
            classe=self.classe,
            matiere=self.matiere,
            titre='Test Chapitre',
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=30)
        )
        self.cours = Cours.objects.create(
            titre='Test Cours',
            chapitre=self.chapitre
        )
        
        now = timezone.now()
        self.quiz = Quiz.objects.create(
            cours=self.cours,
            titre='Test Quiz',
            description='Test Description',
            duree=30,
            tentatives_max=2,
            note_minimale=10.0,
            date_debut=now,
            date_fin=now + timedelta(days=7)
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_type='single',
            texte='Test Question',
            points=1.0
        )
        self.answer = Answer.objects.create(
            question=self.question,
            texte='Test Answer',
            is_correct=True
        )

    def test_quiz_str(self):
        """Test la représentation string du quiz"""
        self.assertEqual(str(self.quiz), 'Test Quiz')

    def test_quiz_is_available(self):
        """Test la disponibilité du quiz"""
        self.assertTrue(self.quiz.is_available())
        
        # Test avec un quiz expiré
        self.quiz.date_fin = timezone.now() - timedelta(days=1)
        self.quiz.save()
        self.assertFalse(self.quiz.is_available())

    def test_quiz_can_student_attempt(self):
        """Test si un étudiant peut tenter le quiz"""
        self.assertTrue(self.quiz.can_student_attempt(self.user))
        
        # Créer deux tentatives
        for _ in range(2):
            QuizAttempt.objects.create(quiz=self.quiz, student=self.user)
        
        self.assertFalse(self.quiz.can_student_attempt(self.user))

class QuizViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Création des objets nécessaires pour le cours
        self.niveau = Niveau.objects.create(nom='Test Niveau')
        self.classe = Classe.objects.create(niveau=self.niveau, numeroClasse=1)
        self.matiere = Matiere.objects.create(nom='Test Matiere')
        self.chapitre = Chapitre.objects.create(
            classe=self.classe,
            matiere=self.matiere,
            titre='Test Chapitre',
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=30)
        )
        self.cours = Cours.objects.create(
            titre='Test Cours',
            chapitre=self.chapitre
        )
        
        now = timezone.now()
        self.quiz = Quiz.objects.create(
            cours=self.cours,
            titre='Test Quiz',
            description='Test Description',
            duree=30,
            tentatives_max=2,
            date_debut=now,
            date_fin=now + timedelta(days=7)
        )

    def test_liste_quiz_view(self):
        """Test la vue de liste des quiz"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('quiz:liste_quiz', args=[self.cours.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/liste_quiz.html')
        self.assertContains(response, 'Test Quiz')

    def test_detail_quiz_view(self):
        """Test la vue de détail d'un quiz"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('quiz:detail_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/detail_quiz.html')

    def test_start_quiz_view(self):
        """Test le démarrage d'un quiz"""
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('quiz:start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertTrue(QuizAttempt.objects.filter(quiz=self.quiz, student=self.user).exists())

class QuestionAnswerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Création des objets nécessaires pour le cours
        self.niveau = Niveau.objects.create(nom='Test Niveau')
        self.classe = Classe.objects.create(niveau=self.niveau, numeroClasse=1)
        self.matiere = Matiere.objects.create(nom='Test Matiere')
        self.chapitre = Chapitre.objects.create(
            classe=self.classe,
            matiere=self.matiere,
            titre='Test Chapitre',
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=30)
        )
        self.cours = Cours.objects.create(
            titre='Test Cours',
            chapitre=self.chapitre
        )
        
        now = timezone.now()
        self.quiz = Quiz.objects.create(
            cours=self.cours,
            titre='Test Quiz',
            duree=30,
            tentatives_max=2,
            date_debut=now,
            date_fin=now + timedelta(days=7)
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_type='single',
            texte='Test Question',
            points=1.0
        )
        self.correct_answer = Answer.objects.create(
            question=self.question,
            texte='Correct Answer',
            is_correct=True
        )
        self.wrong_answer = Answer.objects.create(
            question=self.question,
            texte='Wrong Answer',
            is_correct=False
        )

    def test_question_response_evaluation(self):
        """Test l'évaluation des réponses aux questions"""
        attempt = QuizAttempt.objects.create(quiz=self.quiz, student=self.user)
        response = StudentResponse.objects.create(
            attempt=attempt,
            question=self.question
        )
        response.selected_answers.add(self.correct_answer)
        
        self.assertTrue(response.check_correctness())
        
        response.selected_answers.remove(self.correct_answer)
        response.selected_answers.add(self.wrong_answer)
        
        self.assertFalse(response.check_correctness())

class QuizFormTests(TestCase):
    def setUp(self):
        # Création des objets nécessaires pour le cours
        self.niveau = Niveau.objects.create(nom='Test Niveau')
        self.classe = Classe.objects.create(niveau=self.niveau, numeroClasse=1)
        self.matiere = Matiere.objects.create(nom='Test Matiere')
        self.chapitre = Chapitre.objects.create(
            classe=self.classe,
            matiere=self.matiere,
            titre='Test Chapitre',
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=30)
        )
        self.cours = Cours.objects.create(
            titre='Test Cours',
            chapitre=self.chapitre
        )

    def test_quiz_form_valid(self):
        """Test la validation du formulaire de quiz"""
        now = timezone.now()
        form_data = {
            'titre': 'Test Quiz',
            'description': 'Test Description',
            'duree': 30,
            'tentatives_max': 2,
            'note_minimale': 10.0,
            'date_debut': now,
            'date_fin': now + timedelta(days=7)
        }
        form = QuizForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_quiz_form_invalid(self):
        """Test la validation du formulaire avec données invalides"""
        form_data = {
            'titre': '',  # Titre vide
            'duree': -30,  # Durée négative
        }
        form = QuizForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('titre', form.errors)
        self.assertIn('duree', form.errors)

class StudentResponseFormTests(TestCase):
    def setUp(self):
        # Création des objets nécessaires pour le cours
        self.niveau = Niveau.objects.create(nom='Test Niveau')
        self.classe = Classe.objects.create(niveau=self.niveau, numeroClasse=1)
        self.matiere = Matiere.objects.create(nom='Test Matiere')
        self.chapitre = Chapitre.objects.create(
            classe=self.classe,
            matiere=self.matiere,
            titre='Test Chapitre',
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=30)
        )
        self.cours = Cours.objects.create(
            titre='Test Cours',
            chapitre=self.chapitre
        )
        
        now = timezone.now()
        self.quiz = Quiz.objects.create(
            cours=self.cours,
            titre='Test Quiz',
            duree=30,
            date_debut=now,
            date_fin=now + timedelta(days=7)
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_type='single',
            texte='Test Question'
        )
        self.answer = Answer.objects.create(
            question=self.question,
            texte='Test Answer',
            is_correct=True
        )

    def test_student_response_form(self):
        """Test le formulaire de réponse étudiant"""
        form = StudentResponseForm(question=self.question)
        self.assertIn('selected_answers', form.fields)
        self.assertEqual(form.fields['selected_answers'].queryset.count(), 1)

        # Test pour une question de type texte
        text_question = Question.objects.create(
            quiz=self.quiz,
            question_type='text',
            texte='Text Question'
        )
        form = StudentResponseForm(question=text_question)
        self.assertIn('text_response', form.fields)
