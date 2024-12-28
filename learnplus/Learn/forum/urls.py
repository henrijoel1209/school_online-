from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.liste_sujets, name='liste_sujets'),
    path('cours/<int:cours_id>/sujets/', views.liste_sujets, name='liste_sujets_cours'),
    path('nouveau/', views.nouveau_sujet, name='nouveau_sujet'),
    path('cours/<int:cours_id>/nouveau/', views.nouveau_sujet, name='nouveau_sujet_cours'),
    path('sujet/<slug:slug>/', views.detail_sujet, name='detail_sujet'),
    path('sujet/<slug:slug>/modifier/', views.modifier_sujet, name='modifier_sujet'),
    path('sujet/<slug:slug>/supprimer/', views.supprimer_sujet, name='supprimer_sujet'),
    path('reponse/<int:id>/modifier/', views.modifier_reponse, name='modifier_reponse'),
    path('reponse/<int:id>/supprimer/', views.supprimer_reponse, name='supprimer_reponse'),
]