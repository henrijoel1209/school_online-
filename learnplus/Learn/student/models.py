from django.db import models
from django.contrib.auth.models import User
from school import models as school_models
from quiz import models as quiz_models
from django.utils.text import slugify
from django.db.models import Avg, Sum
from datetime import datetime
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import json


# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User,related_name='student_user',on_delete=models.CASCADE)
    classe = models.ForeignKey(school_models.Classe,on_delete=models.CASCADE,related_name='student_classe', null=True)
    photo = models.ImageField(
        upload_to='images/Student',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    bio = models.TextField(default="Votre bio")
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True,  blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        super(Student, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return self.user.username

    @property
    def get_u_type(self):
        try:
            user = User.objects.get(id=self.user.id)
            cheick = user.student_user
            return True
        except:
            return False

    def get_available_courses(self):
        """Récupérer tous les cours disponibles pour l'étudiant"""
        return school_models.Cours.objects.filter(
            chapitre__classe=self.classe,
            status=True
        )

    def get_available_quizzes(self):
        """Récupérer tous les quiz disponibles pour l'étudiant"""
        return quiz_models.Quiz.objects.filter(
            cours__chapitre__classe=self.classe,
            status=True
        )

    def get_available_devoirs(self):
        """Récupérer tous les devoirs disponibles pour l'étudiant"""
        now = datetime.now()
        return quiz_models.Devoir.objects.filter(
            chapitre__classe=self.classe,
            status=True,
            dateDebut__lte=now,
            dateFermeture__gte=now
        )

    def submit_quiz_response(self, question, reponse_text):
        """Soumettre une réponse à une question de quiz"""
        return StudentResponse.objects.create(
            student=self,
            question=question,
            reponse=reponse_text
        )

    def get_quiz_score(self, quiz):
        """Calculer le score d'un quiz"""
        total_points = sum(question.point for question in quiz.quiz_question.all())
        if total_points == 0:
            return {'earned_points': 0, 'total_points': 0, 'percentage': 0}
        
        earned_points = sum(
            question.point
            for question in quiz.quiz_question.all()
            if self.student_responses.filter(
                question=question,
                is_correct=True
            ).exists()
        )
        
        return {
            'earned_points': earned_points,
            'total_points': total_points,
            'percentage': (earned_points / total_points * 100)
        }

    def get_course_average(self, cours):
        """Calculer la moyenne pour un cours spécifique"""
        quiz_scores = []
        devoir_scores = []
        
        # Scores des quiz
        for quiz in quiz_models.Quiz.objects.filter(cours=cours):
            score = self.get_quiz_score(quiz)
            quiz_scores.append(score['percentage'])
        
        # Scores des devoirs
        for devoir in quiz_models.Devoir.objects.filter(chapitre=cours.chapitre):
            responses = self.student_responses.filter(
                question__quiz__cours=cours
            ).aggregate(avg_score=Avg('score'))
            if responses['avg_score']:
                devoir_scores.append(responses['avg_score'] * devoir.coefficient)
        
        # Calcul de la moyenne
        total_scores = quiz_scores + devoir_scores
        if total_scores:
            return sum(total_scores) / len(total_scores)
        return 0

    def get_overall_average(self):
        """Calculer la moyenne générale de l'étudiant"""
        course_averages = []
        for cours in self.get_available_courses():
            avg = self.get_course_average(cours)
            if avg > 0:
                course_averages.append(avg)
        
        if course_averages:
            return sum(course_averages) / len(course_averages)
        return 0


class StudentResponse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_responses')
    question = models.ForeignKey(quiz_models.Question, on_delete=models.CASCADE, related_name='student_responses')
    reponse = models.TextField()
    score = models.FloatField(default=0)  # Score obtenu pour cette réponse
    is_correct = models.BooleanField(default=False)  # Si la réponse est correcte
    feedback = models.TextField(null=True, blank=True)  # Feedback de l'enseignant
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Vérifier si la réponse est correcte
        correct_answers = self.question.question_reponse.filter(is_True=True)
        self.is_correct = any(answer.reponse == self.reponse for answer in correct_answers)
        
        # Calculer le score si la réponse est correcte
        if self.is_correct:
            self.score = self.question.point
        else:
            self.score = 0
            
        super(StudentResponse, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Student Response'
        verbose_name_plural = 'Student Responses'
        ordering = ['-date_add']  # Les réponses les plus récentes d'abord

    def __str__(self):
        return f"Réponse de {self.student.user.username} à {self.question}"


class StudentGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(school_models.Cours, on_delete=models.CASCADE, related_name='student_grades')
    quiz_scores = models.ManyToManyField(quiz_models.Quiz, through='QuizGrade')
    final_grade = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Note Étudiant'
        verbose_name_plural = 'Notes Étudiants'
        unique_together = ['student', 'course']
        ordering = ['-date_update']

    def __str__(self):
        return f"{self.student.user.username} - {self.course.titre} - {self.final_grade}"

    def calculate_final_grade(self):
        """Calcule la note finale basée sur les quiz"""
        quiz_grades = self.quiz_grades.all()
        if quiz_grades:
            total_score = sum(grade.score for grade in quiz_grades)
            total_possible = sum(grade.quiz.total_points for grade in quiz_grades)
            if total_possible > 0:
                self.final_grade = (total_score / total_possible) * 20  # Note sur 20
            else:
                self.final_grade = 0
        else:
            self.final_grade = 0
        self.save()
        return self.final_grade

    @property
    def grade_percentage(self):
        """Retourne le pourcentage de la note finale"""
        return (self.final_grade / 20) * 100 if self.final_grade else 0

    @property
    def grade_status(self):
        """Retourne le statut de la note"""
        if self.final_grade >= 16:
            return 'Très bien'
        elif self.final_grade >= 14:
            return 'Bien'
        elif self.final_grade >= 12:
            return 'Assez bien'
        elif self.final_grade >= 10:
            return 'Passable'
        else:
            return 'Insuffisant'


class QuizGrade(models.Model):
    student_grade = models.ForeignKey(StudentGrade, on_delete=models.CASCADE, related_name='quiz_grades')
    quiz = models.ForeignKey(quiz_models.Quiz, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    attempts = models.IntegerField(default=0)
    max_score = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Note Quiz'
        verbose_name_plural = 'Notes Quiz'
        unique_together = ['student_grade', 'quiz']
        ordering = ['-date_update']

    def __str__(self):
        return f"{self.student_grade.student.user.username} - {self.quiz.title} - {self.score}"

    def calculate_score(self):
        """Calcule le score du quiz basé sur les réponses de l'étudiant"""
        responses = StudentResponse.objects.filter(
            student=self.student_grade.student,
            question__quiz=self.quiz
        )
        if responses:
            self.score = sum(response.score for response in responses)
            self.max_score = sum(response.question.points for response in responses)
            self.completed = True
            self.date_completed = datetime.now()
            self.save()
            # Mettre à jour la note finale du cours
            self.student_grade.calculate_final_grade()
        return self.score


class StudentAssignment(models.Model):
    """Modèle pour les devoirs"""
    course = models.ForeignKey(school_models.Cours, on_delete=models.CASCADE, related_name='student_assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    max_points = models.FloatField(default=20)
    due_date = models.DateTimeField()
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Devoir'
        verbose_name_plural = 'Devoirs'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.title} - {self.course.titre}"

    @property
    def is_past_due(self):
        """Vérifie si la date limite est dépassée"""
        return timezone.now() > self.due_date

    @property
    def time_remaining(self):
        """Retourne le temps restant avant la date limite"""
        if self.is_past_due:
            return "Date limite dépassée"
        delta = self.due_date - timezone.now()
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        if days > 0:
            return f"{days} jours {hours}h restants"
        elif hours > 0:
            return f"{hours}h {minutes}min restantes"
        else:
            return f"{minutes} minutes restantes"


class StudentAssignmentSubmission(models.Model):
    """Modèle pour les soumissions de devoirs"""
    assignment = models.ForeignKey(StudentAssignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_assignment_submissions')
    submission_file = models.FileField(
        upload_to='assignment_submissions/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'zip', 'rar']
        )]
    )
    submission_text = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Soumis'),
            ('graded', 'Noté'),
            ('late', 'En retard'),
            ('resubmit', 'À refaire')
        ],
        default='submitted'
    )
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Soumission de devoir'
        verbose_name_plural = 'Soumissions de devoirs'
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Si c'est une nouvelle soumission
            # Vérifier si la soumission est en retard
            if self.assignment.is_past_due:
                self.status = 'late'
        super().save(*args, **kwargs)

    @property
    def grade_percentage(self):
        """Retourne le pourcentage de la note"""
        if self.score is not None:
            return (self.score / self.assignment.max_points) * 100
        return 0

    @property
    def grade_status(self):
        """Retourne le statut de la note"""
        if self.score is None:
            return "Non noté"
        percentage = self.grade_percentage
        if percentage >= 80:
            return "Excellent"
        elif percentage >= 60:
            return "Bien"
        elif percentage >= 50:
            return "Moyen"
        else:
            return "Insuffisant"


class CourseProgress(models.Model):
    """Modèle pour suivre la progression d'un étudiant dans un cours"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(school_models.Cours, on_delete=models.CASCADE, related_name='student_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Progression du cours'
        verbose_name_plural = 'Progressions des cours'
        unique_together = ['student', 'course']
        ordering = ['-last_accessed']
        db_table = 'student_courseprogress'

    def __str__(self):
        return f"{self.student.user.username} - {self.course.titre}"

    @property
    def progress_percentage(self):
        """Retourne le pourcentage de progression"""
        completed_chapters = self.chapter_progress.filter(completed=True).count()
        total_chapters = self.chapter_progress.count()
        if total_chapters > 0:
            return (completed_chapters / total_chapters) * 100
        return 0

    @property
    def time_spent(self):
        """Retourne le temps passé sur le cours"""
        chapter_times = self.chapter_progress.aggregate(
            total_time=models.Sum('time_spent')
        )['total_time'] or 0
        return chapter_times


class ChapterProgress(models.Model):
    """Modèle pour suivre la progression d'un étudiant dans un chapitre"""
    course_progress = models.ForeignKey('CourseProgress', on_delete=models.CASCADE, related_name='chapter_progress')
    chapter = models.ForeignKey(school_models.Chapitre, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    time_spent = models.DurationField(default=timezone.timedelta)
    last_position = models.PositiveIntegerField(default=0)  # Position dans le contenu
    completion_date = models.DateTimeField(null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Progression du chapitre'
        verbose_name_plural = 'Progressions des chapitres'
        unique_together = ['course_progress', 'chapter']
        ordering = ['chapter__ordre']
        db_table = 'student_chapterprogress'

    def __str__(self):
        return f"{self.course_progress.student.user.username} - {self.chapter.titre}"

    def update_time_spent(self, duration):
        """Met à jour le temps passé sur le chapitre"""
        self.time_spent += duration
        self.save()

    def mark_complete(self):
        """Marque le chapitre comme complété"""
        if not self.completed:
            self.completed = True
            self.completion_date = timezone.now()
            self.save()
            
            # Enregistrer l'activité
            LearningActivity.objects.create(
                student=self.course_progress.student,
                course=self.course_progress.course,
                chapter=self.chapter,
                activity_type='chapter_complete'
            )


class LearningActivity(models.Model):
    """Modèle pour suivre les activités d'apprentissage"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_activities')
    course = models.ForeignKey(school_models.Cours, on_delete=models.CASCADE)
    chapter = models.ForeignKey(school_models.Chapitre, on_delete=models.CASCADE, null=True, blank=True)
    activity_type = models.CharField(max_length=50, choices=[
        ('course_start', 'Début du cours'),
        ('course_complete', 'Cours terminé'),
        ('chapter_start', 'Début du chapitre'),
        ('chapter_complete', 'Chapitre terminé'),
        ('quiz_start', 'Début du quiz'),
        ('quiz_complete', 'Quiz terminé'),
        ('assignment_submit', 'Devoir soumis'),
        ('grade_received', 'Note reçue')
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(null=True, blank=True)  # Stocké comme JSON sérialisé
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Activité d\'apprentissage'
        verbose_name_plural = 'Activités d\'apprentissage'
        ordering = ['-timestamp']
        db_table = 'student_learningactivity'

    def __str__(self):
        return f"{self.student.user.username} - {self.activity_type} - {self.timestamp}"

    def get_details(self):
        """Récupère les détails au format JSON"""
        if self.details:
            try:
                return json.loads(self.details)
            except json.JSONDecodeError:
                return None
        return None
