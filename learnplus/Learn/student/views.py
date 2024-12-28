from django.shortcuts import render, redirect 
from django.contrib.auth.decorators import login_required
from school import models as school_models
from forum import models as forum_models
from instructor import models as instructor_models
from django.db.models import Q
from chat import models as chat_models
from django.utils.safestring import mark_safe
import json
from django.http import JsonResponse 
from django.contrib.auth.models import User
from . import models
from django.contrib.auth import authenticate, login
from core.decorators import student_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db import models as django_models
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentRegistrationForm, BulkStudentUploadForm
import pandas as pd
from django.contrib.auth.models import User
from .models import Student
from school.models import Classe

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Compte créé avec succès pour {user.username}!')
            return redirect('student:student_list')
    else:
        form = StudentRegistrationForm()
    return render(request, 'student/register.html', {'form': form})

@user_passes_test(is_admin)
def bulk_register_students(request):
    if request.method == 'POST':
        form = BulkStudentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            default_classe = form.cleaned_data['classe']
            
            try:
                df = pd.read_excel(excel_file)
                required_columns = ['Nom', 'Prénom', 'Email']
                
                if not all(col in df.columns for col in required_columns):
                    messages.error(request, 'Le fichier doit contenir les colonnes : Nom, Prénom, Email')
                    return redirect('student:bulk_register')
                
                success_count = 0
                error_count = 0
                
                for _, row in df.iterrows():
                    try:
                        # Créer le nom d'utilisateur à partir du prénom et du nom
                        username = f"{row['Prénom'].lower()}.{row['Nom'].lower()}"
                        # Générer un mot de passe temporaire
                        temp_password = User.objects.make_random_password()
                        
                        # Créer l'utilisateur
                        user = User.objects.create_user(
                            username=username,
                            email=row['Email'],
                            password=temp_password,
                            first_name=row['Prénom'],
                            last_name=row['Nom']
                        )
                        
                        # Créer l'étudiant
                        classe = default_classe
                        if 'Classe' in df.columns and pd.notna(row['Classe']):
                            try:
                                classe = Classe.objects.get(nom=row['Classe'])
                            except Classe.DoesNotExist:
                                classe = default_classe
                        
                        Student.objects.create(
                            user=user,
                            classe=classe,
                            bio=f"Étudiant en {classe.niveau.nom}"
                        )
                        
                        success_count += 1
                        
                        # TODO: Envoyer un email avec les identifiants
                        
                    except Exception as e:
                        error_count += 1
                        continue
                
                messages.success(request, f'{success_count} étudiants créés avec succès. {error_count} erreurs.')
                return redirect('student:student_list')
                
            except Exception as e:
                messages.error(request, f'Erreur lors du traitement du fichier : {str(e)}')
                return redirect('student:bulk_register')
    else:
        form = BulkStudentUploadForm()
    
    return render(request, 'student/bulk_register.html', {'form': form})

@user_passes_test(is_admin)
def student_list(request):
    students = Student.objects.all().select_related('user', 'classe')
    return render(request, 'student/student_list.html', {'students': students})

# Create your views here.
@login_required(login_url = 'login')
def index(request):
    """Vue principale du tableau de bord étudiant"""
    # Redirection des utilisateurs non-étudiants
    if hasattr(request.user, 'instructor'):
        return redirect('dashboard')
    if request.user.is_staff:
        return redirect("/admin/")
        
    try:
        student = request.user.student_user
        # Récupération des cours récents
        cours = school_models.Cours.objects.filter(
            status=True,
            chapitre__classe=student.classe
        ).order_by('-date_add')[:5]
        
        # Récupération des sujets de forum
        forum = forum_models.Sujet.objects.filter(
            cours__chapitre__classe=student.classe
        )[:5]
        forum_count = forum.count()
        
        context = {
            'cours': cours,
            'forum': forum,
            'forum_count': forum_count,
        }
        return render(request, 'pages/fixed-student-dashboard.html', context)
        
    except ObjectDoesNotExist:
        # L'utilisateur n'a pas de profil étudiant
        return redirect("/admin/")
    except Exception as e:
        # Log l'erreur pour le débogage
        print(f"Erreur dans la vue index: {str(e)}")
        # Redirection vers une page d'erreur
        return render(request, 'error.html', {'message': "Une erreur s'est produite"})

@login_required(login_url = 'login')
def payment(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-account-billing-payment-information.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
   
@login_required(login_url = 'login')
def subscription(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-account-billing-subscription.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    
@login_required(login_url = 'login')
def upgrade(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-account-billing-upgrade.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    

@login_required(login_url = 'login')
def edit(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-account-edit.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def edit_basic(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-account-edit-basic.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def edit_profile(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-account-edit-profile.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url = 'login')
def billing(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-billing.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    
# @login_required(login_url = 'login')
# def browse_courses(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.instructor:
#                     return redirect('dashboard')
#             except Exception as e:
#                 print(e)
#                 print("2")
#                 if request.user.student_user:
#                     cours = school_models.Cours.objects.filter(Q(status=True) & Q(chapitre__classe=request.user.student_user.classe))
#                     datas = {
#                                 'all_cours' : all_cours ,
#                            }
#                 return render(request,'pages/fixed-student-browse-courses.html',datas)
#         except Exception as e:
#             print(e)
#             print("3")
#             return redirect("/admin/")
   

@login_required(login_url = 'login')
def cart(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-cart.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def courses(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard') 
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                   
                    datas = {
                                
                           }
                return render(request,'pages/fixed-student-courses.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    
# @login_required(login_url = 'login')
# def dashboard(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.instructor:
#                     return redirect('dashboard')
#             except Exception as e:
#                 print(e)
#                 print("2")
#                 if request.user.student_user:
#                     datas = {

#                            }
#                 return render(request,'pages/fixed-student-dashboard.html',datas)
#         except Exception as e:
#             print(e)
#             print("3")
#             return redirect("/admin/")

@login_required(login_url = 'login')
def earnings(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-earnings.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")



@login_required(login_url = 'login')
def forum(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    forum_general = forum_models.Sujet.objects.filter(cours=None)
                    forum = forum_models.Sujet.objects.filter(cours__chapitre__classe=request.user.student_user.classe)
                    datas = {
                        'forum_general': forum_general,
                        'forum': forum,
                    }
                return render(request,'pages/fixed-student-forum.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")




@login_required(login_url = 'login')
def forum_lesson(request, slug):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    lesson = school_models.Cours.objects.get(slug=slug)
                    datas = {
                        'lesson':lesson,
                    }
                return render(request,'pages/fixed-student-forum-lesson.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")



@login_required(login_url = 'login')
def forum_ask(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-forum-ask.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")




@login_required(login_url = 'login')
def forum_thread(request, slug):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    forum = forum_models.Sujet.objects.get(slug=slug)
                    datas = {
                        "forum": forum,
                    }
                return render(request,'pages/fixed-student-forum-thread.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    

@login_required(login_url = 'login')
def help_center(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-help-center.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    

@login_required(login_url = 'login')
def invoice(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-invoice.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url='login')
def messages(request, classe):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    exist_classe = chat_models.Salon.objects.get(classe=request.user.student_user.classe)
                    info = school_models.Classe.objects.get(id=request.user.student_user.classe.id)
                    instructor = instructor_models.Instructor.objects.get(classe__id=request.user.student_user.classe.id)
                    user_room = ''                    
                    print(user_room)
                    datas = {
                        'instructor':instructor,
                        'info_classe':info,
                        'classe': exist_classe,
                        'classe_json': mark_safe(json.dumps(exist_classe.id)),
                        'username': mark_safe(json.dumps(request.user.username))
                    }
                return render(request,'pages/fixed-student-messages.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    
# @login_required(login_url = 'login')
# def messages_2(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.instructor:
#                     return redirect('dashboard')
#             except Exception as e:
#                 print(e)
#                 print("2")
#                 if request.user.student_user:
#                     datas = {

#                            }
#                 return render(request,'pages/fixed-student-messages-2.html',datas)
#         except Exception as e:
#             print(e)
#             print("3")
#             return redirect("/admin/")

@login_required(login_url = 'login')
def my_courses(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    chapitre = school_models.Chapitre.objects.filter(status=True)
                    cours = school_models.Cours.objects.filter(status=True)
                    all_cours = school_models.Cours.objects.filter(Q(status=True) & Q(chapitre__classe=request.user.student_user.classe))
                    datas = {
                                'chapitre':chapitre, 
                                'cours':cours,
                                'all_cours': all_cours,
                           }
                return render(request,'pages/fixed-student-my-courses.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def quiz_list(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-quiz-list.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def profile(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-profile.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def profile_posts(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-profile-posts.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    

@login_required(login_url = 'login')
def quiz_results(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-quiz-results.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def quizzes(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-quizzes.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    

@login_required(login_url = 'login')
def statement(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-statement.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    

# @login_required(login_url = 'login')
# def student_take_course(request, slug):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.instructor:
#                     return redirect('dashboard')
#             except Exception as e:
#                 print(e)
#                 print("2")
#                 if request.user.student_user:
#                     cours  = school_models.Cours.objets.get(slug=slug)
#                     datas = {
#                         'cours': cours,
#                     }
#                 return render(request,'pages/fixed-student-student-take-course.html',datas)
#         except Exception as e:
#             print(e)
#             print("3")
#             return redirect("/admin/")


@login_required(login_url='login')
def take_course(request, slug):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    cours = school_models.Cours.objects.get(slug=slug)
                    instructor = instructor_models.Instructor.objects.get(classe__id=request.user.student_user.classe.id)
                    datas = {
                        'cours': cours,
                        'instructor' : instructor,
                    }
                return render(request,'pages/fixed-student-take-course.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect('my_courses')
   

@login_required(login_url = 'login')
def take_quiz(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-take-quiz.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

@login_required(login_url = 'login')
def view_course(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-view-course.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")
    
@login_required(login_url = 'login')
def account_edit(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.instructor:
                    return redirect('dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.student_user:
                    datas = {

                           }
                return render(request,'pages/fixed-student-account-edit.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")

        
def update_profil(request):
    nom = request.POST.get("nom")
    prenom = request.POST.get("prenom")
    email = request.POST.get("email")
    bio = request.POST.get("bio")

    try:
        user = User.objects.get(username=request.user.username)
        user.last_name = nom
        user.first_name = prenom
        user.email = email
        user.save()
        student = models.Student.objects.get(user__id=request.user.id)
        student.bio = bio
        student.save()
        try:
            image = request.FILES["file"]
            student.photo = image 
            student.save()

        except:
            pass
        success = True 
        message = "vos informations ont été modifié avec succés"

    except:
        success = False
        message = "une erreur est subvenue lors de la mise à jour"
    data = {
        "success" : success,
        "message" : message,
        }
    return JsonResponse(data,safe=False)

        
def update_password(request):
    last_password = request.POST.get("last_password")
    new_password = request.POST.get("new_password")
    confirm_password = request.POST.get("confirm_password")

    try:
        if not request.user.check_password(last_password):
            success = False
            message = "Ancien mot de passe incorrect"
        elif new_password != confirm_password:
            success = False
            message = "Les mots de passe ne sont pas identiques"
        else:
            user = User.objects.get(username=request.user.username)
            username = user.username
            user.password = new_password
            user.set_password(user.password)
            user.save()
            user = authenticate(username=username, password=new_password)
            login(request, user)
            success = True 
            message = "Mot de passe modfifié avec succès"
    except Exception as e:
        print(e)
        success = False
        message = "une erreur est subvenue lors de la mise à jour"
    data = {
        "success" : success,
        "message" : message,
        }
    return JsonResponse(data,safe=False)

    

        
def post_forum(request):
    titre = request.POST.get("titre")
    question = request.POST.get("question")
    lesson = request.POST.get("lesson")
    val = ""
    try:
        lesson = school_models.Cours.objects.get(id=int(lesson))
        forum = forum_models.Sujet()
        forum.titre = titre
        forum.question = question
        forum.cours = lesson
        forum.user = request.user
        forum.save()
        val = forum.slug
        success = True 
        message = "Votre sujet a bien été ajouté!"
    except Exception as e:
        print(e)
        success = False
        message = "une erreur est subvenue lors de la soumission"
    data = {
        "success" : success,
        "message": message,
        "forum": val,
        }
    return JsonResponse(data,safe=False)

    
def post_forum_g(request):
    titre = request.POST.get("titre")
    question = request.POST.get("question")
    val = ""
    try:
        forum = forum_models.Sujet()
        forum.titre = titre
        forum.question = question
        forum.user = request.user
        forum.save()
        val = forum.slug
        success = True 
        message = "Votre sujet a bien été ajouté!"
    except Exception as e:
        print(e)
        success = False
        message = "une erreur est subvenue lors de la soumission"
    data = {
        "success" : success,
        "message": message,
        "forum": val,
        }
    return JsonResponse(data,safe=False)

@login_required(login_url = 'login')
def grades(request):
    """Vue pour afficher toutes les notes de l'étudiant"""
    student = request.user.student_user
    student_grades = models.StudentGrade.objects.filter(student=student)
    
    # Calculer la moyenne générale
    total_grade = 0
    completed_courses = 0
    for grade in student_grades:
        if grade.completed:
            total_grade += grade.final_grade
            completed_courses += 1
    
    average = total_grade / completed_courses if completed_courses > 0 else 0
    
    context = {
        'student_grades': student_grades,
        'average': average,
        'completed_courses': completed_courses,
        'total_courses': student_grades.count()
    }
    return render(request, 'student/grades.html', context)

@login_required(login_url = 'login')
def course_grade_detail(request, course_slug):
    """Vue pour afficher le détail des notes d'un cours"""
    student = request.user.student_user
    course = get_object_or_404(school_models.Cours, slug=course_slug)
    
    # Récupérer ou créer la note du cours
    student_grade, created = models.StudentGrade.objects.get_or_create(
        student=student,
        course=course
    )
    
    # Récupérer tous les quiz du cours
    quiz_grades = models.QuizGrade.objects.filter(
        student_grade=student_grade
    ).select_related('quiz')
    
    # Calculer les statistiques
    completed_quizzes = quiz_grades.filter(completed=True).count()
    total_quizzes = quiz_grades.count()
    completion_rate = (completed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0
    
    context = {
        'student_grade': student_grade,
        'quiz_grades': quiz_grades,
        'completed_quizzes': completed_quizzes,
        'total_quizzes': total_quizzes,
        'completion_rate': completion_rate
    }
    return render(request, 'student/course_grade_detail.html', context)

@login_required(login_url = 'login')
def quiz_grade_detail(request, quiz_id):
    """Vue pour afficher le détail des notes d'un quiz"""
    student = request.user.student_user
    quiz = get_object_or_404(school_models.Quiz, id=quiz_id)
    course = quiz.cours
    
    # Récupérer la note du cours
    student_grade = get_object_or_404(models.StudentGrade, student=student, course=course)
    
    # Récupérer la note du quiz
    quiz_grade, created = models.QuizGrade.objects.get_or_create(
        student_grade=student_grade,
        quiz=quiz
    )
    
    # Récupérer toutes les réponses de l'étudiant pour ce quiz
    responses = models.StudentResponse.objects.filter(
        student=student,
        question__quiz=quiz
    ).select_related('question')
    
    context = {
        'quiz_grade': quiz_grade,
        'responses': responses,
        'quiz': quiz
    }
    return render(request, 'student/quiz_grade_detail.html', context)

@login_required(login_url = 'login')
def assignments(request):
    """Vue pour afficher tous les devoirs de l'étudiant"""
    student = request.user.student_user
    # Récupérer tous les cours de l'étudiant
    courses = student.courses.all()
    # Récupérer tous les devoirs des cours de l'étudiant
    assignments = models.StudentAssignment.objects.filter(course__in=courses)
    
    # Organiser les devoirs par statut
    pending_assignments = []
    completed_assignments = []
    late_assignments = []
    
    for assignment in assignments:
        submission = models.StudentAssignmentSubmission.objects.filter(
            assignment=assignment,
            student=student
        ).first()
        
        assignment_data = {
            'assignment': assignment,
            'submission': submission,
            'time_remaining': assignment.time_remaining
        }
        
        if submission:
            if submission.status == 'late':
                late_assignments.append(assignment_data)
            else:
                completed_assignments.append(assignment_data)
        elif assignment.is_past_due:
            late_assignments.append(assignment_data)
        else:
            pending_assignments.append(assignment_data)
    
    context = {
        'pending_assignments': pending_assignments,
        'completed_assignments': completed_assignments,
        'late_assignments': late_assignments
    }
    return render(request, 'student/assignments.html', context)

@login_required(login_url = 'login')
def assignment_detail(request, assignment_id):
    """Vue pour afficher et soumettre un devoir"""
    student = request.user.student_user
    assignment = get_object_or_404(models.StudentAssignment, id=assignment_id)
    
    # Vérifier si l'étudiant a accès à ce devoir
    if assignment.course not in student.courses.all():
        messages.error(request, "Vous n'avez pas accès à ce devoir.")
        return redirect('student:assignments')
    
    # Récupérer ou créer la soumission
    submission, created = models.StudentAssignmentSubmission.objects.get_or_create(
        assignment=assignment,
        student=student
    )
    
    if request.method == 'POST':
        # Vérifier si le devoir est en retard
        if assignment.is_past_due and not submission.pk:
            submission.status = 'late'
        
        # Gérer le fichier soumis
        if 'submission_file' in request.FILES:
            submission.submission_file = request.FILES['submission_file']
        
        # Gérer le texte soumis
        submission.submission_text = request.POST.get('submission_text', '')
        submission.save()
        
        messages.success(request, "Votre devoir a été soumis avec succès.")
        return redirect('student:assignment_detail', assignment_id=assignment_id)
    
    context = {
        'assignment': assignment,
        'submission': submission
    }
    return render(request, 'student/assignment_detail.html', context)

@login_required(login_url = 'login')
def delete_submission(request, submission_id):
    """Vue pour supprimer une soumission"""
    submission = get_object_or_404(models.StudentAssignmentSubmission, 
                                 id=submission_id, 
                                 student=request.user.student_user)
    
    if submission.status == 'graded':
        messages.error(request, "Vous ne pouvez pas supprimer une soumission qui a déjà été notée.")
        return redirect('student:assignment_detail', assignment_id=submission.assignment.id)
    
    submission.delete()
    messages.success(request, "Votre soumission a été supprimée avec succès.")
    return redirect('student:assignment_detail', assignment_id=submission.assignment.id)

@login_required(login_url = 'login')
def learning_dashboard(request):
    """Vue pour afficher le tableau de bord d'apprentissage"""
    student = request.user.student_user
    
    # Récupérer toutes les progressions de cours
    course_progress = models.CourseProgress.objects.filter(student=student)
    
    # Calculer les statistiques globales
    total_time = timezone.timedelta()
    completed_courses = 0
    total_activities = 0
    
    for progress in course_progress:
        total_time += progress.time_spent
        if progress.completion_date:
            completed_courses += 1
        total_activities += progress.chapter_progress.filter(completed=True).count()
    
    # Récupérer les activités récentes
    recent_activities = models.LearningActivity.objects.filter(
        student=student
    ).select_related('course', 'chapter')[:10]
    
    context = {
        'course_progress': course_progress,
        'total_time': total_time,
        'completed_courses': completed_courses,
        'total_courses': course_progress.count(),
        'total_activities': total_activities,
        'recent_activities': recent_activities
    }
    return render(request, 'student/learning_dashboard.html', context)

@login_required(login_url = 'login')
def course_progress_detail(request, course_slug):
    """Vue pour afficher la progression détaillée d'un cours"""
    student = request.user.student_user
    course = get_object_or_404(school_models.Cours, slug=course_slug)
    
    # Récupérer ou créer la progression du cours
    progress, created = models.CourseProgress.objects.get_or_create(
        student=student,
        course=course
    )
    
    # Récupérer la progression de chaque chapitre
    chapter_progress = models.ChapterProgress.objects.filter(
        course_progress=progress
    ).select_related('chapter')
    
    # Récupérer les activités du cours
    activities = models.LearningActivity.objects.filter(
        student=student,
        course=course
    ).order_by('-timestamp')[:20]
    
    context = {
        'progress': progress,
        'chapter_progress': chapter_progress,
        'activities': activities
    }
    return render(request, 'student/course_progress_detail.html', context)

@login_required(login_url = 'login')
def update_chapter_progress(request):
    """Vue pour mettre à jour la progression d'un chapitre"""
    if request.method == 'POST' and request.is_ajax():
        chapter_id = request.POST.get('chapter_id')
        position = int(request.POST.get('position', 0))
        duration = int(request.POST.get('duration', 0))  # durée en secondes
        completed = request.POST.get('completed') == 'true'
        
        student = request.user.student_user
        chapter = get_object_or_404(school_models.Chapitre, id=chapter_id)
        course = chapter.cours
        
        # Récupérer ou créer la progression du cours
        course_progress, _ = models.CourseProgress.objects.get_or_create(
            student=student,
            course=course
        )
        
        # Récupérer ou créer la progression du chapitre
        chapter_progress, _ = models.ChapterProgress.objects.get_or_create(
            course_progress=course_progress,
            chapter=chapter
        )
        
        # Mettre à jour la progression
        chapter_progress.update_position(position)
        chapter_progress.update_time_spent(timezone.timedelta(seconds=duration))
        
        if completed and not chapter_progress.completed:
            course_progress.mark_chapter_complete(chapter)
            models.LearningActivity.log_activity(
                student=student,
                course=course,
                chapter=chapter,
                activity_type='chapter_complete'
            )
        
        return JsonResponse({
            'success': True,
            'progress': course_progress.progress_percentage
        })
    
    return JsonResponse({'success': False}, status=400)
