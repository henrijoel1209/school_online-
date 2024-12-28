from django.urls import path
from . import views

app_name = 'school'  # Ajout du namespace

urlpatterns = [
    # URLs d'authentification
    path('', views.home, name="home"),
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup, name="guests_signup"),
    path('forgot-password/', views.forgot_password, name="forgot_password"),
    path('logout/', views.logout_view, name="logout"),
    
    # URLs pour les classes
    path('classes/', views.liste_classes, name="liste_classes"),
    path('classe/<slug:slug>/', views.detail_classe, name="detail_classe"),
    
    # URLs pour les chapitres
    path('chapitres/', views.liste_chapitres, name="liste_chapitres"),
    path('chapitre/<slug:slug>/', views.detail_chapitre, name="detail_chapitre"),
    
    # URLs pour les cours
    path('cours/', views.liste_cours, name="liste_cours"),
    path('cours/<slug:slug>/', views.detail_cours, name="detail_cours"),
    
    # URLs pour les matières
    path('matieres/', views.liste_matieres, name='liste_matieres'),
    path('matieres/ajouter/', views.ajouter_matiere, name='ajouter_matiere'),
    path('matieres/<slug:slug>/modifier/', views.modifier_matiere, name='modifier_matiere'),
    path('matieres/<slug:slug>/supprimer/', views.supprimer_matiere, name='supprimer_matiere'),
    
    # API URLs
    path('api/cours/<slug:slug>/complete/', views.mark_course_completed, name="mark_course_completed"),
]