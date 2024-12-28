from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from chat.models import ChatRoom, MessageChat, PrivateMessage
from student.models import Student
from instructor.models import Instructor
from school.models import Classe, Niveau

class ChatTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Créer un étudiant
        self.student_user = User.objects.create_user(
            username='student_test',
            password='test12345'
        )
        self.student = Student.objects.create(
            user=self.student_user
        )
        
        # Créer un instructeur
        self.instructor_user = User.objects.create_user(
            username='instructor_test',
            password='test12345'
        )
        self.instructor = Instructor.objects.create(
            user=self.instructor_user
        )
        
        # Créer une classe et un salon de chat
        self.niveau = Niveau.objects.create(
            nom='Test Niveau'
        )
        self.classe = Classe.objects.create(
            niveau=self.niveau,
            numeroClasse=1
        )
        self.chat_room = ChatRoom.objects.create(
            name='Test Room',
            is_class_chat=True,
            classe=self.classe
        )
        self.chat_room.participants.add(self.student_user)

    def test_send_message(self):
        """Test l'envoi d'un message dans un salon"""
        self.client.login(username='student_test', password='test12345')
        message_content = "Test message"
        message = MessageChat.objects.create(
            room=self.chat_room,
            sender=self.student_user,
            content=message_content
        )
        self.assertEqual(message.content, message_content)
        self.assertEqual(message.sender, self.student_user)

    def test_private_message(self):
        """Test l'envoi d'un message privé"""
        # Créer un autre utilisateur
        other_user = User.objects.create_user(
            username='other_test',
            password='test12345'
        )
        
        # Envoyer un message privé
        private_message = PrivateMessage.objects.create(
            sender=self.student_user,
            receiver=other_user,
            content="Test private message"
        )
        
        self.assertEqual(private_message.sender, self.student_user)
        self.assertEqual(private_message.receiver, other_user)
        self.assertFalse(private_message.is_read)

    def test_message_privacy(self):
        """Test la confidentialité des messages"""
        # Créer un utilisateur non participant
        non_participant = User.objects.create_user(
            username='non_participant',
            password='test12345'
        )
        
        # Se connecter en tant que non participant
        self.client.login(username='non_participant', password='test12345')
        
        # Essayer d'accéder aux messages du salon
        response = self.client.get(reverse('chat:room_messages', args=[self.chat_room.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
