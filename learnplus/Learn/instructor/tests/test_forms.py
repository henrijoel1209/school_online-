from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from school.forms import ChapitreForm, CoursForm
from school.models import Matiere, Chapitre, Classe, Niveau, Filiere
import datetime
from PIL import Image
import io

class ChapitreFormTest(TestCase):
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

    def test_chapitre_form_valid(self):
        """Test la validation du formulaire avec des données valides"""
        data = {
            'titre': 'Test Chapitre',
            'description': 'Test Description',
            'matiere': self.matiere.id,
            'classe': self.classe.id,
            'date_debut': timezone.now().date(),
            'date_fin': (timezone.now() + datetime.timedelta(days=30)).date(),
            'objectifs': 'Test Objectifs',
            'prerequis': 'Test Prérequis',
            'ordre': 1,
            'status': True
        }
        form = ChapitreForm(data=data)
        self.assertTrue(form.is_valid())

    def test_chapitre_form_invalid_dates(self):
        """Test la validation du formulaire avec des dates invalides"""
        data = {
            'titre': 'Test Chapitre',
            'description': 'Test Description',
            'matiere': self.matiere.id,
            'classe': self.classe.id,
            'date_debut': timezone.now().date(),
            'date_fin': (timezone.now() - datetime.timedelta(days=1)).date(),
            'status': True
        }
        form = ChapitreForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_fin', form.errors)

    def test_chapitre_form_missing_required(self):
        """Test la validation du formulaire avec des champs requis manquants"""
        form = ChapitreForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['titre', 'description', 'matiere', 'classe', 'date_debut', 'date_fin']
        for field in required_fields:
            self.assertIn(field, form.errors)

class CoursFormTest(TestCase):
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

    def test_cours_form_valid(self):
        """Test la validation du formulaire avec des données valides"""
        # Créer une image de test valide
        image = Image.new('RGB', (10, 10), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_file = SimpleUploadedFile(
            "test.jpg",
            image_io.getvalue(),
            content_type="image/jpeg"
        )

        data = {
            'titre': 'Test Cours',
            'description': 'Test Description',
            'chapitre': self.chapitre.id,
            'objectifs': 'Test Objectifs',
            'prerequis': 'Test Prérequis',
            'duree': 2,
            'ordre': 1,
            'status': True
        }
        files = {
            'image': image_file
        }
        form = CoursForm(data=data, files=files, matiere_id=self.matiere.id)
        if not form.is_valid():
            print("Erreurs du formulaire:", form.errors)
        self.assertTrue(form.is_valid())

    def test_cours_form_invalid_file_type(self):
        """Test la validation du formulaire avec un type de fichier invalide"""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain"
        )
        data = {
            'titre': 'Test Cours',
            'description': 'Test Description',
            'chapitre': self.chapitre.id,
            'status': True
        }
        files = {
            'image': invalid_file
        }
        form = CoursForm(data=data, files=files)
        if not form.is_valid():
            print("Erreurs du formulaire:", form.errors)
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_cours_form_file_size_limit(self):
        """Test la validation du formulaire avec un fichier trop volumineux"""
        large_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (5 * 1024 * 1024 + 1),  # 5MB + 1 byte
            content_type="image/jpeg"
        )
        data = {
            'titre': 'Test Cours',
            'description': 'Test Description',
            'chapitre': self.chapitre.id,
            'status': True
        }
        files = {
            'image': large_file
        }
        form = CoursForm(data=data, files=files)
        if not form.is_valid():
            print("Erreurs du formulaire:", form.errors)
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_cours_form_missing_required(self):
        """Test la validation du formulaire avec des champs requis manquants"""
        form = CoursForm(data={})
        if not form.is_valid():
            print("Erreurs du formulaire:", form.errors)
        self.assertFalse(form.is_valid())
        required_fields = ['titre', 'description', 'chapitre']
        for field in required_fields:
            self.assertIn(field, form.errors)
