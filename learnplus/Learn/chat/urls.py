from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('private/', views.private_messages, name='private_messages'),
    path('private/<int:user_id>/', views.private_conversation, name='private_conversation'),
    path('create-class-chat/', views.create_class_chat, name='create_class_chat'),
]