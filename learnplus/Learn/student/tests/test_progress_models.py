from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from student.models import Student, CourseProgress, ChapterProgress, LearningActivity
from school.models import Cours, Chapitre, Matiere, Classe, Niveau, Filiere

class ProgressModelsTest(TestCase):
    def setUp(self):
        # Créer un utilisateur et un étudiant
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.student = Student.objects.create(
            user=self.user,
            bio="Test bio"
        )

        # Créer les objets nécessaires pour le cours
        self.filiere = Filiere.objects.create(
            nom='Test Filiere',
            description='Test Description'
        )
        self.niveau = Niveau.objects.create(
            nom='Test Niveau'
        )
        self.classe = Classe.objects.create(
            niveau=self.niveau,
            numeroClasse=1,
            filiere=self.filiere
        )
        self.matiere = Matiere.objects.create(
            nom='Test Matiere',
            description='Test Description'
        )
        self.chapitre = Chapitre.objects.create(
            classe=self.classe,
            matiere=self.matiere,
            titre='Test Chapter',
            description='Test Description',
            ordre=1
        )
        self.course = Cours.objects.create(
            titre='Test Course',
            chapitre=self.chapitre,
            description='Test Description',
            ordre=1,
            status=True
        )

    def test_course_progress(self):
        # Test création de CourseProgress
        course_progress = CourseProgress.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(course_progress.student, self.student)
        self.assertEqual(course_progress.course, self.course)
        self.assertIsNone(course_progress.completion_date)

    def test_chapter_progress(self):
        # Test création de ChapterProgress
        course_progress = CourseProgress.objects.create(
            student=self.student,
            course=self.course
        )
        chapter_progress = ChapterProgress.objects.create(
            course_progress=course_progress,
            chapter=self.chapitre,
            completed=False,
            last_position=0
        )
        
        # Test marquer comme complété
        chapter_progress.mark_complete()
        self.assertTrue(chapter_progress.completed)
        self.assertIsNotNone(chapter_progress.completion_date)

        # Vérifier que l'activité a été créée
        activity = LearningActivity.objects.filter(
            student=self.student,
            course=self.course,
            chapter=self.chapitre,
            activity_type='chapter_complete'
        ).first()
        self.assertIsNotNone(activity)

    def test_learning_activity(self):
        # Test création de LearningActivity
        activity = LearningActivity.objects.create(
            student=self.student,
            course=self.course,
            chapter=self.chapitre,
            activity_type='course_start'
        )
        self.assertEqual(activity.student, self.student)
        self.assertEqual(activity.course, self.course)
        self.assertEqual(activity.chapter, self.chapitre)
        self.assertEqual(activity.activity_type, 'course_start')

    def test_course_progress_percentage(self):
        # Créer un autre chapitre
        chapter2 = Chapitre.objects.create(
            classe=self.classe,
            matiere=self.matiere,
            titre='Test Chapter 2',
            description='Test Description',
            ordre=2
        )

        # Créer CourseProgress et ChapterProgress
        course_progress = CourseProgress.objects.create(
            student=self.student,
            course=self.course
        )
        
        chapter1_progress = ChapterProgress.objects.create(
            course_progress=course_progress,
            chapter=self.chapitre,
            completed=False
        )
        
        chapter2_progress = ChapterProgress.objects.create(
            course_progress=course_progress,
            chapter=chapter2,
            completed=False
        )

        # Vérifier le pourcentage initial (0%)
        self.assertEqual(course_progress.progress_percentage, 0)

        # Marquer un chapitre comme complété (50%)
        chapter1_progress.mark_complete()
        self.assertEqual(course_progress.progress_percentage, 50)

        # Marquer le deuxième chapitre comme complété (100%)
        chapter2_progress.mark_complete()
        self.assertEqual(course_progress.progress_percentage, 100)
