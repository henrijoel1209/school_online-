from django.db import models
from django.utils.text import slugify
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import Count, Avg
import os
from django.contrib.auth.models import User

class Filiere(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(default="Description de la filière")
    responsable = models.CharField(max_length=255, null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super(Filiere, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Filiere'
        verbose_name_plural = 'Filieres'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def get_classes(self):
        """Retourne les classes de cette filière"""
        return self.classe_filiere.filter(status=True)

    def get_students_count(self):
        """Retourne le nombre total d'étudiants dans cette filière"""
        return sum(classe.student_set.count() for classe in self.get_classes())

class Matiere(models.Model):
    nom = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="images/matiere/", 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    description = models.TextField(default="Description du cours")
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super(Matiere, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Matiere'
        verbose_name_plural = 'Matieres'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def get_chapitres(self):
        """Retourne les chapitres de cette matière"""
        return self.matiere_chapitre.filter(status=True)

    def get_instructors(self):
        """Retourne les enseignants de cette matière"""
        return self.instructor_set.filter(status=True)

class Niveau(models.Model):
    nom = models.CharField(max_length=255)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super(Niveau, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Niveau'
        verbose_name_plural = 'Niveaux'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def get_classes(self):
        """Retourne les classes de ce niveau"""
        return self.classe_niveau.filter(status=True)

class Classe(models.Model):
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='classe_niveau')
    numeroClasse = models.IntegerField()
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='classe_filiere', null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.niveau.nom}-{self.numeroClasse}")
        super(Classe, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['niveau', 'numeroClasse']
        unique_together = ['niveau', 'numeroClasse', 'filiere']

    def __str__(self):
        return f"{self.niveau.nom} {self.numeroClasse}"

    def get_students(self):
        """Retourne les étudiants de cette classe"""
        return self.student_set.filter(status=True)

    def get_chapitres(self):
        """Retourne les chapitres de cette classe"""
        return self.classe_chapitre.filter(status=True)

    def get_average_score(self):
        """Retourne la moyenne générale de la classe"""
        from student.models import StudentResponse
        responses = StudentResponse.objects.filter(
            student__classe=self,
            is_correct__isnull=False
        )
        return responses.aggregate(Avg('score'))['score__avg'] or 0

class Chapitre(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='classe_chapitre', null=True)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='matiere_chapitre')
    titre = models.CharField(max_length=255)
    description = models.TextField(default="Description du chapitre")
    objectifs = models.TextField(blank=True, help_text="Objectifs d'apprentissage du chapitre")
    prerequis = models.TextField(blank=True, help_text="Prérequis nécessaires pour ce chapitre")
    ordre = models.PositiveIntegerField(default=1, help_text="Ordre d'affichage du chapitre")
    video = models.FileField(
        upload_to="ressources/cours", 
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'avi'])]
    )
    duree_en_heure = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(
        upload_to="images/chapitres", 
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    date_debut = models.DateField(null=True)
    date_fin = models.DateField(null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super(Chapitre, self).save(*args, **kwargs)

    def clean(self):
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début")

    class Meta:
        verbose_name = 'Chapitre'
        verbose_name_plural = 'Chapitres'
        ordering = ['matiere', 'ordre', 'date_debut', 'titre']

    def __str__(self):
        return self.titre

    def get_cours(self):
        """Retourne les cours de ce chapitre"""
        return self.cours_chapitre.filter(status=True)

    def get_progress(self, student):
        """Retourne la progression d'un étudiant dans ce chapitre"""
        total_cours = self.get_cours().count()
        if total_cours == 0:
            return 0
        completed_cours = student.completed_courses.filter(
            chapitre=self
        ).count()
        return (completed_cours / total_cours) * 100

class Cours(models.Model):
    titre = models.CharField(max_length=255)
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE, related_name='cours_chapitre')
    description = models.TextField(default="Description du cours")
    objectifs = models.TextField(blank=True, help_text="Objectifs d'apprentissage du cours")
    prerequis = models.TextField(blank=True, help_text="Prérequis nécessaires pour ce cours")
    duree = models.PositiveIntegerField(help_text="Durée estimée en minutes", null=True, blank=True)
    ordre = models.PositiveIntegerField(default=1, help_text="Ordre d'affichage du cours dans le chapitre")
    image = models.ImageField(
        upload_to='images/cours', 
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    video = models.FileField(
        upload_to="ressources/cours",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'avi'])]
    )
    fichier = models.FileField(
        upload_to="ressources/cours",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx'])]
    )
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super(Cours, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        ordering = ['chapitre', 'ordre', 'titre']

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('cours_detail', kwargs={'slug': self.slug})

    def get_video_url(self):
        if self.video:
            return self.video.url
        return None

    def get_fichier_url(self):
        if self.fichier:
            return self.fichier.url
        return None

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    def get_quiz_list(self):
        """Retourne la liste des quiz associés à ce cours"""
        return self.quiz_set.filter(status=True)

    def get_completion_status(self, student):
        """Vérifie si l'étudiant a terminé ce cours"""
        return student.completed_courses.filter(id=self.id).exists()

    def mark_as_completed(self, student):
        """Marque le cours comme terminé pour l'étudiant"""
        student.completed_courses.add(self)

    def unmark_as_completed(self, student):
        """Marque le cours comme non terminé pour l'étudiant"""
        student.completed_courses.remove(self)

    def get_duration_display(self):
        """Retourne la durée formatée (ex: 2h30)"""
        if not self.duree:
            return '0h00'
        hours = int(self.duree / 60)
        minutes = int(self.duree % 60)
        return f"{hours}h{minutes:02d}"

class CourseContent(models.Model):
    CONTENT_TYPES = (
        ('text', 'Texte Enrichi'),
        ('image', 'Image'),
        ('pdf', 'Document PDF'),
        ('video', 'Vidéo'),
    )
    
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    text_content = models.TextField(null=True, blank=True)
    file_content = models.FileField(
        upload_to='course_contents/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf'])]
    )
    video_url = models.URLField(null=True, blank=True)
    order = models.IntegerField(default=0)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Contenu de cours'
        verbose_name_plural = 'Contenus de cours'

    def __str__(self):
        return f"{self.cours.titre} - {self.title}"

    def clean(self):
        if self.content_type in ['image', 'pdf'] and not self.file_content:
            raise ValidationError("Le fichier est requis pour ce type de contenu")
        elif self.content_type == 'video' and not self.video_url:
            raise ValidationError("L'URL de la vidéo est requise pour le type 'vidéo'")
