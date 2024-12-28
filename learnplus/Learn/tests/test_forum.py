from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from forum.models import Sujet, Reponse
from student.models import Student
from school.models import Cours, Chapitre, Matiere

class ForumTests(TestCase):
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
        
        # Créer un cours
        self.matiere = Matiere.objects.create(nom='Test Matiere')
        self.chapitre = Chapitre.objects.create(
            matiere=self.matiere,
            titre='Test Chapitre'
        )
        self.cours = Cours.objects.create(
            chapitre=self.chapitre,
            titre='Test Cours'
        )
        
        # Créer un sujet
        self.sujet = Sujet.objects.create(
            user=self.student_user,
            cours=self.cours,
            titre='Test Sujet',
            question='Test Question?'
        )

    def test_create_sujet(self):
        """Test la création d'un sujet"""
        self.client.login(username='student_test', password='test12345')
        response = self.client.post(reverse('forum:nouveau_sujet'), {
            'titre': 'Nouveau Sujet',
            'question': 'Nouvelle Question?',
            'cours': self.cours.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Sujet.objects.filter(titre='Nouveau Sujet').exists())

    def test_repondre_sujet(self):
        """Test la réponse à un sujet"""
        self.client.login(username='student_test', password='test12345')
        reponse = Reponse.objects.create(
            user=self.student_user,
            sujet=self.sujet,
            reponse='Test Reponse'
        )
        self.assertEqual(reponse.reponse, 'Test Reponse')
        self.assertEqual(reponse.user, self.student_user)

    def test_sujet_search(self):
        """Test la recherche de sujets"""
        # Créer plusieurs sujets
        Sujet.objects.create(
            user=self.student_user,
            cours=self.cours,
            titre='Python Programming',
            question='Question about Python'
        )
        Sujet.objects.create(
            user=self.student_user,
            cours=self.cours,
            titre='Java Programming',
            question='Question about Java'
        )
        
        # Rechercher des sujets
        response = self.client.get(reverse('forum:liste_sujets') + '?q=Python')
        self.assertContains(response, 'Python Programming')
        self.assertNotContains(response, 'Java Programming')
