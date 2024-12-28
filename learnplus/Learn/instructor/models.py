from django.db import models
from django.contrib.auth.models import User
from school import models as school_models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg


# Create your models here.
class Instructor(models.Model):
    user = models.OneToOneField(User,related_name='instructor',on_delete=models.CASCADE)
    contact = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    classe = models.ForeignKey(school_models.Classe, related_name='instructor_classe', on_delete=models.CASCADE, null=True)
    matieres = models.ManyToManyField(school_models.Matiere, related_name='instructors', blank=True)
    photo = models.ImageField(upload_to='images/Instructor')
    bio = models.TextField(default="Votre bio")
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.username)
            slug = base_slug
            n = 1
            while Instructor.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super(Instructor, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructors'

    def __str__(self):
        return self.user.username

    def get_full_name(self):
        """Retourne le nom complet de l'instructeur"""
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_u_type(self):
        try:
            user = User.objects.get(id=self.user.id)
            cheick = user.instructor
            return True
        except:
            return False

    def create_chapitre(self, matiere, titre, description, date_debut, date_fin, **kwargs):
        """Créer un nouveau chapitre pour une matière"""
        if matiere not in self.matieres.all():
            raise ValidationError("Vous n'êtes pas autorisé à créer des chapitres pour cette matière")
        
        return school_models.Chapitre.objects.create(
            matiere=matiere,
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            **kwargs
        )

    def create_cours(self, chapitre, titre, description, **kwargs):
        """Créer un nouveau cours dans un chapitre"""
        if chapitre.matiere not in self.matieres.all():
            raise ValidationError("Vous n'êtes pas autorisé à créer des cours pour ce chapitre")
        
        return school_models.Cours.objects.create(
            chapitre=chapitre,
            titre=titre,
            description=description,
            **kwargs
        )

    def create_quiz(self, cours, titre, temps, date=None):
        """Créer un nouveau quiz pour un cours"""
        from quiz.models import Quiz
        if cours.chapitre.matiere not in self.matieres.all():
            raise ValidationError("Vous n'êtes pas autorisé à créer des quiz pour ce cours")
        
        return Quiz.objects.create(
            cours=cours,
            titre=titre,
            temps=temps,
            date=date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def add_question_to_quiz(self, quiz, question_text, point, type_question='qcm'):
        """Ajouter une question à un quiz"""
        from quiz.models import Question
        if quiz.cours.chapitre.matiere not in self.matieres.all():
            raise ValidationError("Vous n'êtes pas autorisé à modifier ce quiz")
        
        return Question.objects.create(
            quiz=quiz,
            question=question_text,
            point=point,
            typequestion=type_question
        )

    def add_reponse_to_question(self, question, reponse_text, is_correct=False):
        """Ajouter une réponse à une question"""
        from quiz.models import Reponse
        if question.quiz.cours.chapitre.matiere not in self.matieres.all():
            raise ValidationError("Vous n'êtes pas autorisé à modifier cette question")
        
        return Reponse.objects.create(
            question=question,
            reponse=reponse_text,
            is_True=is_correct
        )

    def create_devoir(self, chapitre, sujet, date_debut, date_fermeture, coefficient, support=None):
        """Créer un nouveau devoir"""
        from quiz.models import Devoir
        if chapitre.matiere not in self.matieres.all():
            raise ValidationError("Vous n'êtes pas autorisé à créer des devoirs pour ce chapitre")
        
        return Devoir.objects.create(
            chapitre=chapitre,
            sujet=sujet,
            dateDebut=date_debut,
            dateFermeture=date_fermeture,
            coefficient=coefficient,
            support=support
        )


class Analytics(models.Model):
    """Modèle pour stocker les analyses des performances"""
    instructor = models.ForeignKey('Instructor', on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField(auto_now_add=True)
    
    # Statistiques des étudiants
    total_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0)  # Taux de complétion moyen
    
    # Statistiques des cours
    total_courses = models.IntegerField(default=0)
    total_chapters = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=0)
    
    # Statistiques des évaluations
    average_quiz_score = models.FloatField(default=0)
    total_assignments = models.IntegerField(default=0)
    graded_assignments = models.IntegerField(default=0)
    
    # Statistiques d'engagement
    student_messages = models.IntegerField(default=0)
    forum_posts = models.IntegerField(default=0)
    resource_downloads = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Analytique'
        verbose_name_plural = 'Analytiques'
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.instructor} - {self.date}"
    
    def update_all_stats(self):
        """Met à jour toutes les statistiques"""
        # Statistiques des étudiants
        students = User.objects.filter(groups__name='student').count()
        self.total_students = students
        self.active_students = User.objects.filter(
            groups__name='student',
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Statistiques des cours
        self.total_courses = school_models.Cours.objects.filter(chapitre__instructor=self.instructor).count()
        self.total_chapters = school_models.Chapitre.objects.filter(instructor=self.instructor).count()
        
        # Calcul du taux de complétion (simplifié)
        self.completion_rate = 0
        if self.total_courses > 0:
            self.completion_rate = (self.graded_assignments / self.total_courses) * 100 if self.total_courses else 0
        
        self.save()


class Communication(models.Model):
    """Modèle pour gérer les communications avec les étudiants"""
    instructor = models.ForeignKey('Instructor', on_delete=models.CASCADE, related_name='communications')
    title = models.CharField(max_length=200)
    content = models.TextField()
    recipients = models.ManyToManyField(User, related_name='received_communications')
    attachment = models.FileField(upload_to='communications/', null=True, blank=True)
    date_sent = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=[
        ('announcement', 'Annonce'),
        ('reminder', 'Rappel'),
        ('feedback', 'Feedback'),
        ('notification', 'Notification')
    ])
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Brouillon'),
        ('sent', 'Envoyé'),
        ('scheduled', 'Programmé')
    ], default='draft')
    scheduled_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Communication'
        verbose_name_plural = 'Communications'
        ordering = ['-date_sent']
    
    def __str__(self):
        return self.title
    
    def send(self):
        """Envoie la communication aux destinataires"""
        if self.status == 'draft':
            self.status = 'sent'
            self.date_sent = timezone.now()
            self.save()
    
    def schedule(self, scheduled_date):
        """Programme l'envoi de la communication"""
        self.status = 'scheduled'
        self.scheduled_date = scheduled_date
        self.save()
    
    @property
    def is_sent(self):
        return self.status == 'sent'
    
    @property
    def is_scheduled(self):
        return self.status == 'scheduled'