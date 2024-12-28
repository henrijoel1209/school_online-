from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import ChatRoom, MessageChat, PrivateMessage
from django.contrib.auth.models import User
from school.models import Classe
from student.models import Student
from instructor.models import Instructor

@login_required
def chat_home(request):
    # Récupérer tous les chats de l'utilisateur
    user_chats = ChatRoom.objects.filter(
        participants=request.user,
        status=True
    ).order_by('-date_update')
    
    # Récupérer les messages privés non lus
    unread_messages = PrivateMessage.objects.filter(
        receiver=request.user,
        is_read=False,
        status=True
    ).count()
    
    context = {
        'chats': user_chats,
        'unread_messages': unread_messages
    }
    return render(request, 'chat/chat_home.html', context)

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, status=True)
    
    # Vérifier que l'utilisateur est participant
    if request.user not in room.participants.all():
        return redirect('chat:chat_home')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        file = request.FILES.get('file')
        
        if content or file:
            message = MessageChat.objects.create(
                room=room,
                sender=request.user,
                content=content,
                file_attachment=file
            )
            
            # Si c'est une requête AJAX, renvoyer le message en JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'content': message.content,
                        'sender': message.sender.username,
                        'date': message.date_add.strftime('%H:%M'),
                        'file': message.file_attachment.url if message.file_attachment else None
                    }
                })
    
    messages = room.messages.filter(status=True).order_by('date_add')
    context = {
        'room': room,
        'messages': messages
    }
    return render(request, 'chat/chat_room.html', context)

@login_required
def private_messages(request):
    # Récupérer toutes les conversations privées
    sent_messages = PrivateMessage.objects.filter(sender=request.user, status=True)
    received_messages = PrivateMessage.objects.filter(receiver=request.user, status=True)
    
    # Créer une liste unique des utilisateurs avec qui on a conversé
    contacts = set()
    for msg in sent_messages:
        contacts.add(msg.receiver)
    for msg in received_messages:
        contacts.add(msg.sender)
    
    context = {
        'contacts': contacts
    }
    return render(request, 'chat/private_messages.html', context)

@login_required
def private_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Marquer tous les messages non lus comme lus
    PrivateMessage.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        file = request.FILES.get('file')
        
        if content or file:
            message = PrivateMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                file_attachment=file
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'content': message.content,
                        'date': message.date_add.strftime('%H:%M'),
                        'file': message.file_attachment.url if message.file_attachment else None
                    }
                })
    
    # Récupérer tous les messages entre les deux utilisateurs
    messages = PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user),
        status=True
    ).order_by('date_add')
    
    context = {
        'other_user': other_user,
        'messages': messages
    }
    return render(request, 'chat/private_conversation.html', context)

@login_required
def create_class_chat(request):
    if not hasattr(request.user, 'instructor'):
        return redirect('chat:chat_home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        classe_id = request.POST.get('classe')
        
        if name and classe_id:
            classe = get_object_or_404(Classe, id=classe_id)
            chat_room = ChatRoom.objects.create(
                name=name,
                is_class_chat=True,
                classe=classe
            )
            
            # Ajouter l'instructeur
            chat_room.participants.add(request.user)
            
            # Ajouter tous les étudiants de la classe
            students = Student.objects.filter(classe=classe)
            for student in students:
                chat_room.participants.add(student.user)
            
            return redirect('chat:chat_room', room_id=chat_room.id)
    
    # Récupérer les classes de l'instructeur
    classes = request.user.instructor.classe.all()
    context = {
        'classes': classes
    }
    return render(request, 'chat/create_class_chat.html', context)
