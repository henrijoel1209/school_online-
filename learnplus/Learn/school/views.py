from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as login_request, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.urls import reverse
from .models import *
from student.models import Student
from instructor.models import Instructor

def home(request):
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'student_user'):
                return redirect('student:dashboard')
            elif hasattr(request.user, 'instructor'):
                return redirect('instructor:dashboard')
            else:
                return redirect("/admin/")
        except Exception as e:
            messages.error(request, f"Erreur d'authentification: {str(e)}")
            return render(request, 'pages/guest-login.html')
    return render(request, 'pages/guest-login.html')

def login_view(request):
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'student_user'):
                return redirect('student:dashboard')
            elif hasattr(request.user, 'instructor'):
                return redirect('instructor:dashboard')
            else:
                return redirect("/admin/")
        except Exception as e:
            messages.error(request, f"Erreur d'authentification: {str(e)}")
            return redirect('school:login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs')
            return redirect('school:login')
            
        user = authenticate(username=username, password=password)
        if user is not None:
            login_request(request, user)
            messages.success(request, 'Connexion réussie!')
            
            if hasattr(user, 'student_user'):
                return redirect('student:dashboard')
            elif hasattr(user, 'instructor'):
                return redirect('instructor:dashboard')
            else:
                return redirect("/admin/")
        else:
            messages.error(request, 'Identifiants invalides')
            return redirect('school:login')
            
    return render(request, 'pages/guest-login.html')

def signup(request):
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'student_user'):
                return redirect('student:dashboard')
            elif hasattr(request.user, 'instructor'):
                return redirect('instructor:dashboard')
            else:
                return redirect("/admin/")
        except Exception as e:
            messages.error(request, f"Erreur d'authentification: {str(e)}")
            return redirect('signup')
            
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        
        if not all([username, email, password, confirm_password, role]):
            messages.error(request, 'Veuillez remplir tous les champs')
            return redirect('signup')
            
        if password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas')
            return redirect('signup')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà')
            return redirect('signup')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email existe déjà')
            return redirect('signup')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        
        if role == 'student':
            Student.objects.create(user=user)
            messages.success(request, 'Compte étudiant créé avec succès!')
        elif role == 'instructor':
            Instructor.objects.create(user=user)
            messages.success(request, 'Compte enseignant créé avec succès!')
        else:
            user.delete()
            messages.error(request, 'Rôle invalide')
            return redirect('signup')
            
        login_request(request, user)
        return redirect('school:login')
        
    return render(request, 'pages/guest-signup.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Veuillez entrer votre email')
            return redirect('forgot_password')
            
        try:
            user = User.objects.get(email=email)
            # TODO: Implémenter la logique de réinitialisation du mot de passe
            messages.success(request, 'Un email de réinitialisation a été envoyé')
            return redirect('school:login')
        except User.DoesNotExist:
            messages.error(request, 'Aucun compte associé à cet email')
            
    return render(request, 'pages/guest-forgot-password.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie!')
    return redirect('school:login')

# Views pour les classes
@login_required
def liste_classes(request):
    if hasattr(request.user, 'instructor'):
        classes = Classe.objects.filter(status=True)
    else:
        classes = request.user.student_user.classe.filter(status=True)
    
    context = {
        'classes': classes
    }
    return render(request, 'pages/liste_classes.html', context)

@login_required
def detail_classe(request, slug):
    classe = get_object_or_404(Classe, slug=slug, status=True)
    
    if not hasattr(request.user, 'instructor') and request.user.student_user.classe != classe:
        return HttpResponseForbidden("Vous n'avez pas accès à cette classe")
        
    context = {
        'classe': classe,
        'chapitres': classe.get_chapitres(),
        'students': classe.get_students(),
        'average_score': classe.get_average_score()
    }
    return render(request, 'pages/detail_classe.html', context)

# Views pour les chapitres
@login_required
def liste_chapitres(request):
    if hasattr(request.user, 'instructor'):
        chapitres = Chapitre.objects.filter(status=True)
    else:
        chapitres = Chapitre.objects.filter(
            classe=request.user.student_user.classe,
            status=True
        )
    
    context = {
        'chapitres': chapitres
    }
    return render(request, 'pages/liste_chapitres.html', context)

@login_required
def detail_chapitre(request, slug):
    chapitre = get_object_or_404(Chapitre, slug=slug, status=True)
    
    if not hasattr(request.user, 'instructor') and chapitre.classe != request.user.student_user.classe:
        return HttpResponseForbidden("Vous n'avez pas accès à ce chapitre")
        
    context = {
        'chapitre': chapitre,
        'cours': chapitre.get_cours()
    }
    if hasattr(request.user, 'student_user'):
        context['progress'] = chapitre.get_progress(request.user.student_user)
        
    return render(request, 'pages/detail_chapitre.html', context)

# Views pour les cours
@login_required
def liste_cours(request):
    if hasattr(request.user, 'instructor'):
        cours = Cours.objects.filter(status=True)
    else:
        cours = Cours.objects.filter(
            chapitre__classe=request.user.student_user.classe,
            status=True
        )
    
    context = {
        'cours': cours
    }
    return render(request, 'pages/liste_cours.html', context)

@login_required
def detail_cours(request, slug):
    cours = get_object_or_404(Cours, slug=slug, status=True)
    
    if not hasattr(request.user, 'instructor') and cours.chapitre.classe != request.user.student_user.classe:
        return HttpResponseForbidden("Vous n'avez pas accès à ce cours")
        
    context = {
        'cours': cours,
        'contents': cours.get_contents(),
        'quizzes': cours.get_quizzes(),
        'assignments': cours.get_assignments(),
        'forum_topics': cours.get_forum_topics(),
        'completion_rate': cours.get_completion_rate()
    }
    return render(request, 'pages/detail_cours.html', context)

# API views
@login_required
def mark_course_completed(request, slug):
    if request.method == 'POST':
        cours = get_object_or_404(Cours, slug=slug, status=True)
        student = request.user.student_user
        
        if cours.chapitre.classe != student.classe:
            return JsonResponse({'error': "Vous n'avez pas accès à ce cours"}, status=403)
            
        student.completed_courses.add(cours)
        return JsonResponse({'success': True})
        
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# Views pour les matières
from django.contrib.auth.decorators import user_passes_test
from .forms import MatiereForm

@login_required
@user_passes_test(lambda u: u.is_superuser)
def liste_matieres(request):
    matieres = Matiere.objects.all()
    return render(request, 'school/matiere/liste.html', {'matieres': matieres})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ajouter_matiere(request):
    if request.method == 'POST':
        form = MatiereForm(request.POST, request.FILES)
        if form.is_valid():
            matiere = form.save()
            messages.success(request, f'La matière {matiere.nom} a été créée avec succès.')
            return redirect('school:liste_matieres')
    else:
        form = MatiereForm()
    return render(request, 'school/matiere/form.html', {
        'form': form,
        'title': 'Ajouter une matière'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def modifier_matiere(request, slug):
    matiere = get_object_or_404(Matiere, slug=slug)
    if request.method == 'POST':
        form = MatiereForm(request.POST, request.FILES, instance=matiere)
        if form.is_valid():
            matiere = form.save()
            messages.success(request, f'La matière {matiere.nom} a été modifiée avec succès.')
            return redirect('school:liste_matieres')
    else:
        form = MatiereForm(instance=matiere)
    return render(request, 'school/matiere/form.html', {
        'form': form,
        'matiere': matiere,
        'title': 'Modifier une matière'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def supprimer_matiere(request, slug):
    matiere = get_object_or_404(Matiere, slug=slug)
    if request.method == 'POST':
        nom = matiere.nom
        matiere.delete()
        messages.success(request, f'La matière {nom} a été supprimée avec succès.')
        return redirect('school:liste_matieres')
    return render(request, 'school/matiere/supprimer.html', {'matiere': matiere})
