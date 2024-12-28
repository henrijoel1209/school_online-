from django.db import models
from school import models as school_models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from student.models import Student
from instructor.models import Instructor

# Create your models here.
class Salon(models.Model):
    """Model definition for Salon."""

    nom = models.CharField(max_length=250, null=True)
    classe = models.OneToOneField(school_models.Classe, on_delete=models.CASCADE, related_name="class_room", null=True)
    date_add = models.DateTimeField(auto_now=False, auto_now_add=True)
    date_upd =models.DateTimeField(auto_now=True, auto_now_add=False)
    status = models.BooleanField(default=True)

    @receiver(post_save, sender=school_models.Classe)
    def create_salon(sender, instance, created, **kwargs):
        if created:
            Salon.objects.create(classe=instance)

    @receiver(post_save, sender=school_models.Classe)
    def save_salon(sender, instance, created, **kwargs):
        instance.class_room.save()

    class Meta:
        """Meta definition for Salon."""

        verbose_name = 'Salon'
        verbose_name_plural = 'Salons'

    def __str__(self):
        """Unicode representation of Salon."""
        return self.nom

class Message(models.Model):
    """Model definition for Message."""
    auteur = models.ForeignKey(User, related_name="auteur_message", on_delete=models.CASCADE)
    message = models.TextField()
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name="salon")
    status = models.BooleanField(default=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateField( auto_now=True)

    class Meta:
        """Meta definition for Message."""

        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        """Unicode representation of Message."""
        return self.auteur.username

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_add']
        verbose_name = 'Message Privé'
        verbose_name_plural = 'Messages Privés'

    def __str__(self):
        return f"Message de {self.sender} à {self.receiver}"

    @property
    def short_content(self):
        """Retourne une version courte du contenu pour l'aperçu"""
        return self.content[:50] + '...' if len(self.content) > 50 else self.content

    def mark_as_read(self):
        """Marque le message comme lu"""
        if not self.is_read:
            self.is_read = True
            self.save()

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    is_class_chat = models.BooleanField(default=False)
    classe = models.ForeignKey('school.Classe', on_delete=models.CASCADE, null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Salon de Chat'
        verbose_name_plural = 'Salons de Chat'

    def __str__(self):
        return self.name

    @property
    def last_message(self):
        """Retourne le dernier message de la conversation"""
        return self.messages.order_by('-date_add').first()

class MessageChat(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['date_add']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."