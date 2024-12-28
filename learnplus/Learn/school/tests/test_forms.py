from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from school.forms import ChapitreForm, CoursForm
from school.models import Matiere, Classe, Chapitre, Niveau, Filiere
from datetime import date
from django.utils import timezone

class ChapitreFormTest(TestCase):
    def setUp(self):
        # Créer un niveau
        self.niveau = Niveau.objects.create(
            nom="Niveau Test"
        )
        
        # Créer une filière
        self.filiere = Filiere.objects.create(
            nom="Filière Test",
            description="Description test"
        )
        
        self.matiere = Matiere.objects.create(
            nom="Test Matière",
            description="Description test"
        )
        
        self.classe = Classe.objects.create(
            niveau=self.niveau,
            numeroClasse=1,
            filiere=self.filiere
        )

    def test_chapitre_form_valid_data(self):
        """Test avec des données valides"""
        # Créer un petit GIF valide
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )
        image = SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')
        
        today = date.today()
        
        form_data = {
            'matiere': self.matiere.id,
            'classe': self.classe.id,
            'titre': "Test Chapitre",
            'description': "Description test",
            'ordre': 1,
            'status': True,
            'date_debut': today,
            'date_fin': today
        }
        form = ChapitreForm(data=form_data, files={'image': image})
        
        if not form.is_valid():
            print("Form errors:", form.errors)  # Pour le débogage
            
        self.assertTrue(form.is_valid())

    def test_chapitre_form_large_image(self):
        """Test avec une image trop grande"""
        # Créer un fichier qui dépasse 5MB
        large_file = b'x' * (6 * 1024 * 1024)  # 6MB
        image = SimpleUploadedFile('large.jpg', large_file, content_type='image/jpeg')
        
        form_data = {
            'titre': "Test Chapitre",
            'description': "Description test",
            'matiere': self.matiere.id,
            'status': True,
            'date_debut': timezone.now().date(),
            'date_fin': timezone.now().date() + timezone.timedelta(days=7),
        }
        
        form = ChapitreForm(data=form_data, files={'image': image})
        self.assertFalse(form.is_valid())
        self.assertIn("dépasser 5MB", form.errors['image'][0])

    def test_chapitre_form_default_ordre(self):
        """Test que le champ ordre a bien une valeur par défaut de 1"""
        form = ChapitreForm()
        self.assertEqual(
            form.fields['ordre'].widget.attrs.get('value'),
            1
        )

class CoursFormTest(TestCase):
    def setUp(self):
        # Créer un niveau
        self.niveau = Niveau.objects.create(
            nom="Niveau Test"
        )
        
        # Créer une filière
        self.filiere = Filiere.objects.create(
            nom="Filière Test",
            description="Description test"
        )
        
        self.matiere = Matiere.objects.create(
            nom="Test Matière",
            description="Description test"
        )
        
        self.classe = Classe.objects.create(
            niveau=self.niveau,
            numeroClasse=1,
            filiere=self.filiere
        )
        
        self.chapitre = Chapitre.objects.create(
            matiere=self.matiere,
            classe=self.classe,
            titre="Test Chapitre",
            description="Description test",
            ordre=1
        )

    def test_cours_form_valid_data(self):
        """Test avec des données valides"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')
        
        today = date.today()
        
        form_data = {
            'chapitre': self.chapitre.id,
            'titre': "Test Cours",
            'description': "Description test",
            'ordre': 1,
            'status': True,
            'date_debut': today,
            'date_fin': today
        }
        form = CoursForm(data=form_data, files={'image': image})
        self.assertTrue(form.is_valid())

    def test_cours_form_large_video(self):
        """Test avec une vidéo trop grande"""
        # Créer une vidéo de plus de 100MB
        large_file = b'x' * (101 * 1024 * 1024)  # 101MB
        video = SimpleUploadedFile('large.mp4', large_file, content_type='video/mp4')
        
        today = date.today()
        
        form_data = {
            'chapitre': self.chapitre.id,
            'titre': "Test Cours",
            'description': "Description test",
            'ordre': 1,
            'status': True,
            'date_debut': today,
            'date_fin': today
        }
        form = CoursForm(data=form_data, files={'video': video})
        self.assertFalse(form.is_valid())
        self.assertIn("La vidéo ne doit pas dépasser 100MB", form.errors['video'])

    def test_cours_form_large_fichier(self):
        """Test avec un fichier trop grand"""
        # Créer un fichier de plus de 20MB
        large_file = b'x' * (21 * 1024 * 1024)  # 21MB
        fichier = SimpleUploadedFile('large.pdf', large_file, content_type='application/pdf')
        
        today = date.today()
        
        form_data = {
            'chapitre': self.chapitre.id,
            'titre': "Test Cours",
            'description': "Description test",
            'ordre': 1,
            'status': True,
            'date_debut': today,
            'date_fin': today
        }
        form = CoursForm(data=form_data, files={'fichier': fichier})
        self.assertFalse(form.is_valid())
        self.assertIn("Le fichier ne doit pas dépasser 20MB", form.errors['fichier'])

    def test_cours_form_invalid_file_type(self):
        """Test avec un type de fichier non supporté"""
        invalid_file = b'x' * 1024  # 1KB
        fichier = SimpleUploadedFile('test.txt', invalid_file, content_type='text/plain')
        
        today = date.today()
        
        form_data = {
            'chapitre': self.chapitre.id,
            'titre': "Test Cours",
            'description': "Description test",
            'ordre': 1,
            'status': True,
            'date_debut': today,
            'date_fin': today
        }
        form = CoursForm(data=form_data, files={'fichier': fichier})
        self.assertFalse(form.is_valid())
        self.assertIn("Le type de fichier n'est pas supporté", form.errors['fichier'])

    def test_cours_form_default_ordre(self):
        """Test que le champ ordre a bien une valeur par défaut de 1"""
        form = CoursForm()
        self.assertEqual(
            form.fields['ordre'].widget.attrs.get('value'),
            1
        )
