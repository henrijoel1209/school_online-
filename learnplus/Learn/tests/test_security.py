import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from school.models import Chapitre, Cours, Filiere, Niveau, Classe, Matiere
from student.models import Student
from instructor.models import Instructor

class TestSecurity(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Créer une classe
        self.niveau = Niveau.objects.create(nom='Test Niveau Sec')
        self.filiere = Filiere.objects.create(nom='Test Filière Sec')
        self.classe = Classe.objects.create(
            niveau=self.niveau,
            filiere=self.filiere,
            numeroClasse=1
        )
        
        # Créer un étudiant
        self.student = Student.objects.create(
            user=self.user,
            classe=self.classe
        )

    def test_authentication_required(self):
        """Test que les pages protégées nécessitent une authentification"""
        protected_urls = [
            reverse('instructor:dashboard'),
            reverse('school:liste_cours'),
            reverse('school:liste_chapitres'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse('school:login')))

    def test_role_based_access(self):
        """Test que les rôles sont correctement appliqués"""
        # Se connecter en tant qu'étudiant
        self.client.login(username='testuser', password='testpass123')
        
        # Essayer d'accéder à une page instructeur
        response = self.client.get(reverse('instructor:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirection vers le dashboard étudiant

    def test_csrf_protection(self):
        """Test que la protection CSRF est active"""
        # Désactiver temporairement le middleware CSRF pour ce test
        self.client = Client(enforce_csrf_checks=True)
        
        # Se connecter
        self.client.login(username='testuser', password='testpass123')
        
        # Essayer de faire une requête POST sans CSRF token
        response = self.client.post(
            reverse('school:login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        
        # La requête devrait être rejetée avec un code 403
        self.assertEqual(response.status_code, 403)

    def test_file_upload_security(self):
        """Test la sécurité des uploads de fichiers"""
        self.client.login(username='testuser', password='testpass123')
        
        # Créer un faux fichier malveillant
        malicious_file = SimpleUploadedFile(
            "evil.php",
            b"<?php echo 'malicious code'; ?>",
            content_type="application/x-php"
        )
        
        # Essayer d'uploader le fichier malveillant
        response = self.client.post(reverse('school:upload_file'), {
            'file': malicious_file
        })
        
        # Vérifier que l'upload est rejeté
        self.assertEqual(response.status_code, 400)
        self.assertIn("Format de fichier non autorisé", response.content.decode())

    def test_sql_injection_prevention(self):
        """Test la prévention des injections SQL"""
        self.client.login(username='testuser', password='testpass123')
        
        # Créer quelques données de test
        matiere = Matiere.objects.create(
            nom='Test Matière Sec',
            description='Description',
            status=True
        )
        chapitre = Chapitre.objects.create(
            titre='Test Chapitre Sec',
            description='Description',
            matiere=matiere,
            status=True
        )
        
        # Tester avec une tentative d'injection SQL
        malicious_query = "' OR '1'='1"
        response = self.client.get(
            reverse('school:liste_cours') + f'?search={malicious_query}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Tous les cours")
