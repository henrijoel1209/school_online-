from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.core.paginator import Paginator
from school import models as school_models
from school.forms import ChapitreForm, CoursForm
from quiz import models as quiz_models
from forum import models as forum_models
from chat import models as chat_models
from . import models
from django.utils.safestring import mark_safe
import json
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from datetime import datetime

# Create your views here.
@login_required(login_url='/login/')
def dashboard(request):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    matiere = school_models.Matiere.objects.filter(status=True)
    context = {
        'matiere': matiere,
    }
    return render(request, 'pages/instructor-dashboard.html', context)


@login_required(login_url='/login/')
def account_edit(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                return render(request,'pages/instructor-account-edit.html',datas)
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
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                 return render(request,'pages/instructor-browse-courses.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


# @login_required(login_url = 'login')
# def carts(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                 return render(request,'pages/instructor-cart.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


@login_required(login_url='/login/')
def course_add(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard') 
            except Exception as e:
                print(e)
                print("2")

                if request.user.instructor:
                    matiere = school_models.Matiere.objects.filter(status=True)
                    datas = {
                        'matiere':matiere,
                    }
                    return render(request,'pages/instructor-course-add.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def course_edit(request, slug):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")

                if request.user.instructor:
                    matiere = school_models.Matiere.objects.filter(status=True)
                    chapitre = school_models.Chapitre.objects.get(slug=slug)

                    datas = {
                        'matiere':matiere,
                        'chapitre':chapitre,
                    }
                    return render(request,'pages/instructor-course-edit.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def courses(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard') 
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    Chapitre = school_models.Chapitre.objects.filter(Q(status=True) & Q(classe=request.user.instructor.classe))
                    datas = {
                            'Chapitre' : Chapitre ,
                           }
                    return render(request,'pages/instructor-courses.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def matiere(request, slug):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    Chapitre = school_models.Chapitre.objects.filter(Q(status=True) & Q(classe=request.user.instructor.classe) & Q(matiere__slug=slug))
                    datas = {
                            'Chapitre' : Chapitre ,
                           }
                    return render(request,'pages/instructor-cours-chap.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def earnings(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-account-edit.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


# @login_required(login_url = 'login')
# def edit_invoice(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
#                 print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-edit-invoice.html',datas)
#         except Exception as e:
#             print(e)
#             print("3")
#             return redirect("/admin/")


@login_required(login_url='/login/')
def forum(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    forum_general = forum_models.Sujet.objects.filter(cours=None)
                    forum = forum_models.Sujet.objects.filter(cours__chapitre__classe=request.user.instructor.classe)
                    datas = {
                        'forum_general': forum_general,
                        'forum': forum,
                    }
                    return render(request,'pages/instructor-forum.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def forum_ask(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-forum-ask.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def forum_thread(request, slug):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    forum = forum_models.Sujet.objects.get(slug=slug)
                    datas = {
                        "forum": forum,
                    }
                    return render(request,'pages/instructor-forum-thread.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


# @login_required(login_url = 'login')
# def invoice(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
#                 print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-invoice.html',datas)
#         except Exception as e:
#             print(e)
#             print("3")
#             return redirect("/admin/")


# @login_required(login_url = 'login')
# def invoice_settings(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-invoice-settings.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


@login_required(login_url='/login/')
def lesson_add(request, slug):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    chapitre = school_models.Chapitre.objects.get(slug=slug)
                    datas = {
                        'chapitre': chapitre,
                           }
                    return render(request,'pages/instructor-lesson-add.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def lesson_edit(request, slug, id):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    chapitre = school_models.Chapitre.objects.get(id=id)
                    cours = school_models.Cours.objects.get(slug=slug)

                    datas = {
                        'chapitre': chapitre,
                        'cours': cours,
                    }
                    return render(request,'pages/instructor-lesson-edit.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def messages(request, classe):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    exist_classe = chat_models.Salon.objects.get(classe=request.user.instructor.classe)
                    info = school_models.Classe.objects.get(id=request.user.instructor.classe.id)
                    user_room = ''                    
                    print(user_room)
                    datas = {
                        'info_classe': info,
                        'classe': exist_classe,
                        'classe_json': mark_safe(json.dumps(exist_classe.id)),
                        'username': mark_safe(json.dumps(request.user.username))
                    }
                    return render(request,'pages/instructor-messages.html',datas)
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
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
#                 print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-messages-2.html',datas)
#         except Exception as e:
#             print(e)
#             print("3")
#             return redirect("/admin/")


# @login_required(login_url = 'login')
# def my_courses(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-my-courses.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


@login_required(login_url='/login/')
def profile(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-profile.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def quiz_edit(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-quiz-edit.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def quiz_add(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-quiz-add.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


# @login_required(login_url = 'login')
# def quiz_results(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-quiz-results.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


@login_required(login_url='/login/')
def quizzes(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-quizzes.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


@login_required(login_url='/login/')
def review_quiz(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-review-quiz.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


# @login_required(login_url = 'login')
# def take_course(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-take-course.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


# @login_required(login_url = 'login')
# def take_quiz(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-take-quiz.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


# @login_required(login_url = 'login')
# def view_course(request):
#     if request.user.is_authenticated:
#         try:
#             try:
#                 print("1")
#                 if request.user.student_user:
#                     return redirect('student:dashboard')
#             except Exception as e:
# print(e)
#                 print("2")
#                 if request.user.instructor:
#                     datas = {

#                            }
#                     return render(request,'pages/instructor-view-course.html',datas)
#         except Exception as e:
# print(e)
#             print("3")
#             return redirect("/admin/")


@login_required(login_url='/login/')
def statement(request):
    if request.user.is_authenticated:
        try:
            try:
                print("1")
                if request.user.student_user:
                    return redirect('student:dashboard')
            except Exception as e:
                print(e)
                print("2")
                if request.user.instructor:
                    datas = {

                           }
                    return render(request,'pages/instructor-statement.html',datas)
        except Exception as e:
            print(e)
            print("3")
            return redirect("/admin/")


# fonction pour recuperer les donnees d'un cours et enregistrer

""" Add and update chapitre """
def post_cours(request):
    title = request.POST.get("title") 
    matiere = request.POST.get("matiere")
    date_fin = request.POST.get("date_fin")
    description = request.POST.get("description")
    date_debut = request.POST.get("date_debut")
    duration = request.POST.get("duration")
    id = request.POST.get("id")
    chapitre = ''

    try:
        chapitre = school_models.Chapitre.objects.get(id=id)
        chapitre.titre = title
        chapitre.duree_en_heure = duration
        chapitre.description = description
        matiere = school_models.Matiere.objects.get(id=int(matiere))
        chapitre.matiere = matiere
        chapitre.classe = request.user.instructor.classe
        chapitre.save()
        try:
            video = request.FILES["file"]
            image = request.FILES["image"]
            chapitre.video = video
            chapitre.image = image
            chapitre.save()
        except :
            pass
        try:
            chapitre.date_debut = date_debut
            chapitre.save()
        except:
            pass
        try:
            chapitre.date_fin = date_fin
            chapitre.save()
        except:
            pass
        success = True 
        message = 'mis à jour effectué  avec succés'
    except:
        chapitre = school_models.Chapitre()
        try:
            video = request.FILES["file"]
            image = request.FILES["image"]
            chapitre.video = video
            chapitre.image = image
            chapitre.save()
        except :
            pass
        chapitre.titre = title
        chapitre.duree_en_heure = duration
        chapitre.date_debut = date_debut
        chapitre.date_fin = date_fin
        chapitre.description = description
        matiere = school_models.Matiere.objects.get(id=int(matiere))
        chapitre.matiere = matiere
        chapitre.classe = request.user.instructor.classe
        chapitre.save()
        success = True 
        message = 'chapitre ajouté avec succés'
    data = {
        'success' : success,
        'message' : message,
        'slug': chapitre.slug,
    }
    return JsonResponse(data,safe=False)



""" delete chapitre"""
def delete_chapitre(request):
    id = request.POST.get("id")
    try:
        chapitre = school_models.Chapitre.objects.get(id=int(id))
        chapitre.delete()
        success = True
        message = "La leçon a bien été supprimée"
    except Exception as e:
        print(e)
        success = False
        message = "Une erreur s'est produite"
    data = {
        'success' : success,
        'message' : message,
    }
    return JsonResponse(data,safe=False)





""" add and update lesson """
def post_lesson(request):
    title = request.POST.get("title")
    chapitre = request.POST.get("chapitre")
    description = request.POST.get("description")
    id = request.POST.get("id")

    try:
        cours = school_models.Cours.objects.get(Q(id=int(id)) & Q(chapitre__id=int(chapitre)))

        try:
            video = request.FILES["file"]
            image = request.FILES["image"]
            pdf = request.FILES["pdf"]
            cours.video = video
            cours.image = image
            cours.pdf = pdf
        except:
            pass
        cours.titre = title
        cours.description = description
        cours.save()
        success = True 
        message = 'mis à jour effectué  avec succés'
    except:
        cours = school_models.Cours()
        try:
            chapitre = school_models.Chapitre.objects.get(id=int(chapitre))
            video = request.FILES["file"]
            image = request.FILES["image"]
            pdf = request.FILES["pdf"]
            cours.video = video
            cours.chapitre = chapitre
            cours.image = image
            cours.description = description
            cours.pdf = pdf
            cours.titre = title
            cours.save()
            success = True 
            message = 'cours ajouté avec succés'
        except Exception as e:
            print(e)
            success = False
            message = "Une erreur s'est produite"
    data = {
        'success' : success,
        'message' : message,
    }
    return JsonResponse(data,safe=False)



""" delete lesson"""
def delete_lesson(request):
    id = request.POST.get("id")
    try:
        lesson = school_models.Cours.objects.get(id=int(id))
        lesson.delete()
        success = True
        message = "La leçon a bien été supprimée"
    except Exception as e:
        success = False
        message = "Une erreur s'est produite"
    data = {
        'success' : success,
        'message' : message,
    }
    return JsonResponse(data,safe=False)

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
        instructor = models.Instructor.objects.get(user__id=request.user.id)
        instructor.bio = bio
        instructor.save()
        try:
            image = request.FILES["file"]
            instructor.photo = image 
            instructor.save()

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

"""  Post forum """

def post_forum(request):
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

@login_required(login_url='/login/')
def chapters(request):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    # Récupérer les filtres
    matiere_id = request.GET.get('matiere')
    status = request.GET.get('status')
    search = request.GET.get('search')

    # Filtrer les chapitres
    chapitres = school_models.Chapitre.objects.filter(
        Q(status=True) & Q(classe=request.user.instructor.classe)
    )

    if matiere_id:
        chapitres = chapitres.filter(matiere_id=matiere_id)
    if status:
        chapitres = chapitres.filter(status=status == 'active')
    if search:
        chapitres = chapitres.filter(
            Q(titre__icontains=search) | 
            Q(description__icontains=search)
        )

    # Pagination
    paginator = Paginator(chapitres, 10)
    page = request.GET.get('page')
    chapitres = paginator.get_page(page)

    context = {
        'chapitres': chapitres,
        'matieres': school_models.Matiere.objects.filter(status=True),
        'selected_matiere': matiere_id,
        'status': status,
        'search': search
    }
    return render(request, 'instructor/chapters/list.html', context)

@login_required(login_url='/login/')
def chapter_add(request):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    if request.method == 'POST':
        form = ChapitreForm(request.POST, request.FILES)
        if form.is_valid():
            chapitre = form.save(commit=False)
            chapitre.classe = request.user.instructor.classe
            chapitre.save()
            django_messages.success(request, 'Le chapitre a été créé avec succès')
            return redirect('instructor:chapters')
    else:
        form = ChapitreForm()

    context = {
        'form': form,
        'matieres': school_models.Matiere.objects.filter(status=True)
    }
    return render(request, 'instructor/chapters/add.html', context)

@login_required(login_url='/login/')
def chapter_edit(request, slug):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    chapitre = get_object_or_404(
        school_models.Chapitre, 
        slug=slug,
        classe=request.user.instructor.classe
    )

    if request.method == 'POST':
        form = ChapitreForm(request.POST, request.FILES, instance=chapitre)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Le chapitre a été modifié avec succès')
            return redirect('instructor:chapters')
    else:
        form = ChapitreForm(instance=chapitre)

    context = {
        'form': form,
        'chapitre': chapitre,
        'matieres': school_models.Matiere.objects.filter(status=True)
    }
    return render(request, 'instructor/chapters/edit.html', context)

@login_required(login_url='/login/')
def chapter_delete(request, slug):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    chapitre = get_object_or_404(
        school_models.Chapitre, 
        slug=slug,
        classe=request.user.instructor.classe
    )
    chapitre.delete()
    django_messages.success(request, 'Le chapitre a été supprimé avec succès')
    return redirect('instructor:chapters')

@login_required(login_url='/login/')
def courses(request):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    # Récupérer les filtres
    chapitre_id = request.GET.get('chapitre')
    matiere_id = request.GET.get('matiere')
    status = request.GET.get('status')
    search = request.GET.get('search')

    # Filtrer les cours
    cours = school_models.Cours.objects.filter(
        chapitre__classe=request.user.instructor.classe
    )

    if chapitre_id:
        cours = cours.filter(chapitre_id=chapitre_id)
    if matiere_id:
        cours = cours.filter(chapitre__matiere_id=matiere_id)
    if status:
        cours = cours.filter(status=status == 'active')
    if search:
        cours = cours.filter(
            Q(titre__icontains=search) | 
            Q(description__icontains=search)
        )

    # Pagination
    paginator = Paginator(cours, 10)
    page = request.GET.get('page')
    cours = paginator.get_page(page)

    context = {
        'cours': cours,
        'chapitres': school_models.Chapitre.objects.filter(
            classe=request.user.instructor.classe,
            status=True
        ),
        'matieres': school_models.Matiere.objects.filter(status=True),
        'selected_chapitre': chapitre_id,
        'selected_matiere': matiere_id,
        'status': status,
        'search': search
    }
    return render(request, 'instructor/courses/list.html', context)

@login_required(login_url='/login/')
def course_add(request):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    if request.method == 'POST':
        form = CoursForm(
            request.POST, 
            request.FILES,
            matiere_id=request.POST.get('matiere')
        )
        if form.is_valid():
            cours = form.save()
            django_messages.success(request, 'Le cours a été créé avec succès')
            return redirect('instructor:courses')
    else:
        matiere_id = request.GET.get('matiere')
        form = CoursForm(matiere_id=matiere_id)

    context = {
        'form': form,
        'matieres': school_models.Matiere.objects.filter(status=True)
    }
    return render(request, 'instructor/courses/add.html', context)

@login_required(login_url='/login/')
def course_edit(request, slug):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    cours = get_object_or_404(
        school_models.Cours,
        slug=slug,
        chapitre__classe=request.user.instructor.classe
    )

    if request.method == 'POST':
        form = CoursForm(
            request.POST,
            request.FILES,
            matiere_id=request.POST.get('matiere'),
            instance=cours
        )
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Le cours a été modifié avec succès')
            return redirect('instructor:courses')
    else:
        form = CoursForm(
            matiere_id=cours.chapitre.matiere_id,
            instance=cours
        )

    context = {
        'form': form,
        'cours': cours,
        'matieres': school_models.Matiere.objects.filter(status=True)
    }
    return render(request, 'instructor/courses/edit.html', context)

@login_required(login_url='/login/')
def course_delete(request, slug):
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')

    cours = get_object_or_404(
        school_models.Cours,
        slug=slug,
        chapitre__classe=request.user.instructor.classe
    )
    cours.delete()
    django_messages.success(request, 'Le cours a été supprimé avec succès')
    return redirect('instructor:courses')

@login_required(login_url='/login/')
def analytics_dashboard(request):
    """Vue pour le tableau de bord analytique"""
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')
    
    # Récupérer ou créer les analytics pour aujourd'hui
    analytics, created = models.Analytics.objects.get_or_create(
        instructor=request.user.instructor,
        date=timezone.now().date()
    )
    
    # Mettre à jour toutes les statistiques
    analytics.update_all_stats()
    
    # Récupérer l'historique des analytics
    analytics_history = models.Analytics.objects.filter(
        instructor=request.user.instructor
    ).order_by('-date')[:30]  # 30 derniers jours
    
    context = {
        'analytics': analytics,
        'history': analytics_history
    }
    return render(request, 'instructor/analytics_dashboard.html', context)

@login_required(login_url='/login/')
def communications(request):
    """Vue pour gérer les communications"""
    if not hasattr(request.user, 'instructor'):
        return redirect('student:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        comm_type = request.POST.get('type')
        recipients = request.POST.getlist('recipients')
        attachment = request.FILES.get('attachment')
        scheduled_date = request.POST.get('scheduled_date')
        
        # Créer la communication
        communication = models.Communication.objects.create(
            instructor=request.user.instructor,
            title=title,
            content=content,
            type=comm_type,
            attachment=attachment
        )
        
        # Ajouter les destinataires
        communication.recipients.set(recipients)
        
        # Programmer ou envoyer
        if scheduled_date:
            scheduled_datetime = timezone.datetime.strptime(
                scheduled_date,
                '%Y-%m-%dT%H:%M'
            ).replace(tzinfo=timezone.get_current_timezone())
            communication.schedule(scheduled_datetime)
        else:
            communication.send()
        
        django_messages.success(request, 'Communication envoyée avec succès')
        return redirect('instructor:communications')
    
    # Récupérer toutes les communications
    communications = models.Communication.objects.filter(
        instructor=request.user.instructor
    ).order_by('-date_sent')
    
    # Récupérer tous les étudiants pour le formulaire
    students = school_models.Student.objects.filter(
        classe__instructor=request.user.instructor
    )
    
    context = {
        'communications': communications,
        'students': students
    }
    return render(request, 'instructor/communications.html', context)
