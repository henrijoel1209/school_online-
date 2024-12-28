from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from school.models import Matiere, Chapitre, Cours, Classe, Niveau, Filiere
from instructor.models import Instructor
from django.utils import timezone
import datetime

class InstructorViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testinstructor',
            password='testpass123',
            first_name='Test',
            last_name='Instructor'
        )
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.matiere = Matiere.objects.create(
            nom='Test Matière',
            description='Test Description',
            image=image,
            status=True
        )
        self.niveau = Niveau.objects.create(
            nom='Test Niveau'
        )
        self.filiere = Filiere.objects.create(
            nom='Test Filière',
            description='Test Description'
        )
        self.classe = Classe.objects.create(
            niveau=self.niveau,
            numeroClasse=1,
            filiere=self.filiere
        )
        photo = SimpleUploadedFile(
            "test_photo.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.instructor = Instructor.objects.create(
            user=self.user,
            contact='0123456789',
            adresse='Test Adresse',
            classe=self.classe,
            photo=photo,
            bio='Test Bio'
        )
        self.instructor.matieres.add(self.matiere)
        self.chapitre = Chapitre.objects.create(
            titre='Test Chapitre',
            description='Test Description',
            matiere=self.matiere,
            classe=self.classe,
            date_debut=timezone.now(),
            date_fin=timezone.now() + datetime.timedelta(days=30),
            status=True
        )
        self.cours = Cours.objects.create(
            titre='Test Cours',
            description='Test Description',
            chapitre=self.chapitre,
            status=True
        )

    def test_dashboard_view_authenticated(self):
        """Test l'accès au dashboard pour un instructeur authentifié"""
        # Créer un nouvel utilisateur pour ce test
        user = User.objects.create_user(
            username='testinstructor2',
            password='testpass123',
            first_name='Test2',
            last_name='Instructor2'
        )
        instructor = Instructor.objects.create(
            user=user,
            contact='0123456789',
            adresse='Test Adresse',
            classe=self.classe,
            bio='Test Bio'
        )
        instructor.matieres.add(self.matiere)
        
        self.client.login(username='testinstructor2', password='testpass123')
        response = self.client.get(reverse('instructor:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/instructor-dashboard.html')

    def test_dashboard_view_unauthenticated(self):
        """Test la redirection pour un utilisateur non authentifié"""
        response = self.client.get(reverse('instructor:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('school:login')))

    def test_chapitre_list_view(self):
        """Test la vue de liste des chapitres"""
        self.client.login(username='testinstructor', password='testpass123')
        response = self.client.get(reverse('instructor:chapters'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor/chapters/list.html')
        self.assertContains(response, 'Test Chapitre')

    def test_chapitre_create_view(self):
        """Test la création d'un chapitre"""
        self.client.login(username='testinstructor', password='testpass123')
        data = {
            'titre': 'Nouveau Chapitre',
            'description': 'Description du nouveau chapitre',
            'matiere': self.matiere.id,
            'classe': self.classe.id,
            'date_debut': timezone.now().date(),
            'date_fin': (timezone.now() + datetime.timedelta(days=30)).date(),
            'ordre': 1,
            'status': True
        }
        response = self.client.post(reverse('instructor:chapter_add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Chapitre.objects.filter(titre='Nouveau Chapitre').exists())

    def test_chapitre_update_view(self):
        """Test la modification d'un chapitre"""
        self.client.login(username='testinstructor', password='testpass123')
        data = {
            'titre': 'Chapitre Modifié',
            'description': 'Description modifiée',
            'matiere': self.matiere.id,
            'classe': self.classe.id,
            'date_debut': timezone.now().date(),
            'date_fin': (timezone.now() + datetime.timedelta(days=30)).date(),
            'ordre': 1,
            'status': True
        }
        response = self.client.post(
            reverse('instructor:chapter_edit', kwargs={'slug': self.chapitre.slug}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.chapitre.refresh_from_db()
        self.assertEqual(self.chapitre.titre, 'Chapitre Modifié')

    def test_chapitre_delete_view(self):
        """Test la suppression d'un chapitre"""
        self.client.login(username='testinstructor', password='testpass123')
        response = self.client.post(
            reverse('instructor:chapter_delete', kwargs={'slug': self.chapitre.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Chapitre.objects.filter(pk=self.chapitre.pk).exists())

    def test_cours_list_view(self):
        """Test la vue de liste des cours"""
        self.client.login(username='testinstructor', password='testpass123')
        response = self.client.get(reverse('instructor:courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor/courses/list.html')
        self.assertContains(response, self.cours.titre)

    def test_cours_create_view(self):
        """Test la création d'un cours"""
        self.client.login(username='testinstructor', password='testpass123')
        data = {
            'titre': 'Nouveau Cours',
            'description': 'Description du nouveau cours',
            'chapitre': self.chapitre.id,
            'ordre': 1,
            'status': True
        }
        response = self.client.post(reverse('instructor:course_add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cours.objects.filter(titre='Nouveau Cours').exists())

    def test_cours_update_view(self):
        """Test la modification d'un cours"""
        self.client.login(username='testinstructor', password='testpass123')
        data = {
            'titre': 'Cours Modifié',
            'description': 'Description modifiée',
            'chapitre': self.chapitre.id,
            'ordre': 1,
            'status': True
        }
        response = self.client.post(
            reverse('instructor:course_edit', kwargs={'slug': self.cours.slug}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.cours.refresh_from_db()
        self.assertEqual(self.cours.titre, 'Cours Modifié')

    def test_cours_delete_view(self):
        """Test la suppression d'un cours"""
        self.client.login(username='testinstructor', password='testpass123')
        response = self.client.post(
            reverse('instructor:course_delete', kwargs={'slug': self.cours.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cours.objects.filter(pk=self.cours.pk).exists())
