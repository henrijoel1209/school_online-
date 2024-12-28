from django.db import models
from django.contrib.auth.models import User
from school.models import Cours
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

def get_default_end_date():
    return timezone.now() + timedelta(days=7)

class Quiz(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='quizzes')
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duree = models.IntegerField(help_text="Durée en minutes", default=30)
    tentatives_max = models.IntegerField(default=1)
    note_minimale = models.FloatField(default=10.0)
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(default=get_default_end_date)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'

    def __str__(self):
        return self.titre

    def clean(self):
        if self.date_fin <= self.date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début")

    def is_available(self):
        """Vérifie si le quiz est disponible actuellement"""
        now = timezone.now()
        return self.date_debut <= now <= self.date_fin and self.status

    def get_student_attempts(self, student):
        """Retourne le nombre de tentatives d'un étudiant"""
        return self.attempts.filter(student=student).count()

    def can_student_attempt(self, student):
        """Vérifie si l'étudiant peut tenter le quiz"""
        return (self.is_available() and 
                self.get_student_attempts(student) < self.tentatives_max)

class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Choix unique'),
        ('multiple', 'Choix multiple'),
        ('text', 'Réponse texte'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single')
    texte = models.TextField(default='')
    points = models.FloatField(default=1.0)
    explanation = models.TextField(blank=True, help_text="Explication de la réponse correcte")
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.texte[:50]}..."

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    texte = models.TextField(default='')
    is_correct = models.BooleanField(default=False)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.texte

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.titre}"

    @property
    def is_completed(self):
        return self.completed_at is not None

    def calculate_score(self):
        """Calcule le score de la tentative"""
        total_points = 0
        earned_points = 0
        
        for response in self.responses.all():
            question = response.question
            total_points += question.points
            if response.is_correct:
                earned_points += question.points
        
        self.score = earned_points
        self.save()

class StudentResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, blank=True)
    text_response = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Réponse de {self.attempt.student.username}"

    def check_correctness(self):
        """Vérifie si la réponse est correcte"""
        if self.question.question_type == 'text':
            # La correction manuelle est nécessaire
            return None
        
        correct_answers = set(self.question.answers.filter(is_correct=True))
        selected = set(self.selected_answers.all())
        
        self.is_correct = correct_answers == selected
        self.save()
        return self.is_correct

class Assignment(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='assignments')
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_debut = models.DateTimeField(default=timezone.now)
    date_limite = models.DateTimeField(default=get_default_end_date)
    points_max = models.FloatField(default=20.0)
    fichier_instruction = models.FileField(upload_to='assignments/', null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Devoir'
        verbose_name_plural = 'Devoirs'
        ordering = ['-date_limite']

    def __str__(self):
        return self.titre

    def clean(self):
        if self.date_limite <= self.date_debut:
            raise ValidationError("La date limite doit être postérieure à la date de début")

    def is_available(self):
        """Vérifie si le devoir est disponible"""
        now = timezone.now()
        return self.date_debut <= now <= self.date_limite and self.status

    def time_remaining(self):
        """Retourne le temps restant avant la date limite"""
        if not self.is_available():
            return timedelta(0)
        return self.date_limite - timezone.now()

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    fichier_reponse = models.FileField(upload_to='assignment_submissions/')
    commentaire = models.TextField(null=True, blank=True)
    note = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Soumission de devoir'
        verbose_name_plural = 'Soumissions de devoirs'
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.titre}"

    @property
    def is_late(self):
        """Vérifie si la soumission est en retard"""
        return self.submitted_at > self.assignment.date_limite

    def calculate_penalty(self):
        """Calcule la pénalité pour les soumissions en retard"""
        if not self.is_late or self.note is None:
            return 0
        
        delay_hours = (self.submitted_at - self.assignment.date_limite).total_seconds() / 3600
        penalty_points = min(delay_hours * 0.5, 5)  # 0.5 point par heure, max 5 points
        return penalty_points