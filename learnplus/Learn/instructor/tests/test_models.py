from django.test import TestCase
from django.contrib.auth.models import User
from school.models import Matiere, Chapitre, Cours, Classe, Niveau, Filiere
from instructor.models import Instructor
from django.utils import timezone
import datetime

class InstructorModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testinstructor',
            password='testpass123'
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
        self.instructor = Instructor.objects.create(
            user=self.user,
            classe=self.classe
        )

    def test_instructor_str(self):
        """Test la représentation en chaîne de l'instructeur"""
        self.assertEqual(str(self.instructor), self.user.username)

    def test_instructor_get_full_name(self):
        """Test la méthode get_full_name de l'instructeur"""
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        self.assertEqual(self.instructor.get_full_name(), 'John Doe')

class ChapitreModelTest(TestCase):
    def setUp(self):
        self.matiere = Matiere.objects.create(
            nom='Test Matière',
            description='Test Description',
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
        self.chapitre = Chapitre.objects.create(
            titre='Test Chapitre',
            description='Test Description',
            matiere=self.matiere,
            classe=self.classe,
            date_debut=timezone.now(),
            date_fin=timezone.now() + datetime.timedelta(days=30),
            status=True
        )

    def test_chapitre_str(self):
        """Test la représentation en chaîne du chapitre"""
        self.assertEqual(str(self.chapitre), self.chapitre.titre)

    def test_chapitre_slug_generation(self):
        """Test la génération automatique du slug"""
        self.assertEqual(
            self.chapitre.slug,
            'test-chapitre'
        )

    def test_chapitre_ordering(self):
        """Test l'ordre des chapitres"""
        chapitre2 = Chapitre.objects.create(
            titre='Test Chapitre 2',
            description='Test Description',
            matiere=self.matiere,
            classe=self.classe,
            date_debut=timezone.now(),
            date_fin=timezone.now() + datetime.timedelta(days=30),
            ordre=2,
            status=True
        )
        chapitres = Chapitre.objects.all()
        self.assertEqual(chapitres[0], self.chapitre)  # ordre=1 (défaut)
        self.assertEqual(chapitres[1], chapitre2)  # ordre=2

class CoursModelTest(TestCase):
    def setUp(self):
        self.matiere = Matiere.objects.create(
            nom='Test Matière',
            description='Test Description',
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

    def test_cours_str(self):
        """Test la représentation en chaîne du cours"""
        self.assertEqual(str(self.cours), self.cours.titre)

    def test_cours_slug_generation(self):
        """Test la génération automatique du slug"""
        self.assertEqual(
            self.cours.slug,
            'test-cours'
        )

    def test_cours_ordering(self):
        """Test l'ordre des cours"""
        cours2 = Cours.objects.create(
            titre='Test Cours 2',
            description='Test Description',
            chapitre=self.chapitre,
            ordre=2,
            status=True
        )
        cours = Cours.objects.all()
        self.assertEqual(cours[0], self.cours)  # ordre=1 (défaut)
        self.assertEqual(cours[1], cours2)  # ordre=2

    def test_cours_get_duration_display(self):
        """Test l'affichage de la durée du cours"""
        self.cours.duree = 150  # 2h30 en minutes
        self.cours.save()
        self.assertEqual(self.cours.get_duration_display(), '2h30')

        self.cours.duree = 60
        self.cours.save()
        self.assertEqual(self.cours.get_duration_display(), '1h00')
