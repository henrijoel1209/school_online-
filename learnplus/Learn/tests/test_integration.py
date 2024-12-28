import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from school.models import Filiere, Niveau, Classe, Matiere, Chapitre, Cours
from student.models import Student
from instructor.models import Instructor
from quiz.models import Quiz, Question, Answer
from django.core.files.uploadedfile import SimpleUploadedFile

class TestUserFlows(TestCase):
    def setUp(self):
        # Créer un utilisateur étudiant
        self.student_user = User.objects.create_user(
            username='student_test',
            password='test12345'
        )
        self.student = Student.objects.create(user=self.student_user)
        
        # Créer un utilisateur instructeur
        self.instructor_user = User.objects.create_user(
            username='instructor_test',
            password='test12345'
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user)
        
        # Créer les données nécessaires
        self.filiere = Filiere.objects.create(nom='Test Filiere')
        self.niveau = Niveau.objects.create(nom='Test Niveau')
        self.classe = Classe.objects.create(
            niveau=self.niveau,
            numeroClasse=1,
            filiere=self.filiere
        )
        
        # Mettre à jour l'instructeur avec la classe
        self.instructor.classe = self.classe
        self.instructor.save()
        
        # Créer une matière avec image
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.matiere = Matiere.objects.create(
            nom='Test Matiere',
            description='Test Description',
            image=image
        )
        self.instructor.matieres.add(self.matiere)
        
        # Créer un chapitre
        self.chapitre = Chapitre.objects.create(
            titre='Test Chapitre',
            description='Test Description',
            matiere=self.matiere,
            classe=self.classe,
            date_debut='2024-01-01',
            date_fin='2024-12-31'
        )
        
        # Créer un cours
        self.cours = Cours.objects.create(
            titre='Test Cours',
            description='Test Description',
            chapitre=self.chapitre
        )
        
        # Créer un client pour les tests
        self.client = Client()

    def test_student_dashboard_access(self):
        """Test l'accès au tableau de bord étudiant"""
        # Se connecter en tant qu'étudiant
        self.client.login(username='student_test', password='test12345')
        
        # Accéder au tableau de bord
        response = self.client.get(reverse('student_dashboard'))
        
        # Vérifier que l'accès est autorisé
        self.assertEqual(response.status_code, 200)

    def test_instructor_course_management(self):
        """Test la gestion des cours par l'instructeur"""
        # Créer un instructeur avec tous les champs requis
        instructor_user = User.objects.create_user(
            username='testinstructor2',
            password='testpass123',
            email='instructor2@test.com'
        )
        
        # Créer une classe pour l'instructeur
        niveau = Niveau.objects.create(nom='Test Niveau Integration 2')
        filiere = Filiere.objects.create(nom='Test Filière Integration 2')
        classe = Classe.objects.create(
            niveau=niveau,
            filiere=filiere,
            numeroClasse=1
        )
        
        # Créer une photo de test
        photo = SimpleUploadedFile(
            name='test_photo.jpg',
            content=b'test_content',
            content_type='image/jpeg'
        )
        
        # Créer le profil instructeur complet
        instructor = Instructor.objects.create(
            user=instructor_user,
            classe=classe,
            photo=photo
        )
        
        # Se connecter
        self.client.login(username='testinstructor2', password='testpass123')
        
        # Accéder au dashboard instructeur
        response = self.client.get(reverse('instructor:dashboard'))
        self.assertEqual(response.status_code, 200)
