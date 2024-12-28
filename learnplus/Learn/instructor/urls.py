from django.urls import path
from . import views

app_name = 'instructor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('account_edit', views.account_edit, name='account-edit'), 

    # Chapitres
    path('chapters/', views.chapters, name='chapters'),
    path('chapters/add/', views.chapter_add, name='chapter_add'),
    path('chapters/<slug:slug>/edit/', views.chapter_edit, name='chapter_edit'),
    path('chapters/<slug:slug>/delete/', views.chapter_delete, name='chapter_delete'),

    # Cours
    path('courses/', views.courses, name='courses'),
    path('courses/add/', views.course_add, name='course_add'),
    path('courses/<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('courses/<slug:slug>/delete/', views.course_delete, name='course_delete'),

    # Autres URLs
    path('matiere/<slug>', views.matiere, name='matiere'), 
    path('forum', views.forum, name='forum'),
    path('forum_ask', views.forum_ask, name='forum-ask'),
    path('forum_thread/<slug>', views.forum_thread, name='forum-thread'),
    path('lesson-add/<slug>', views.lesson_add, name='lesson-add'),
    path('lesson-edit/<id>/<slug>', views.lesson_edit, name='lesson-edit'),
    path('messages/<str:classe>/', views.messages, name='messages'),
    path('profile', views.profile, name='profile'),
    path('quiz_edit', views.quiz_edit, name='quiz-edit'),
    path('quiz_add', views.quiz_add, name='quiz-add'),
    path('review_quiz', views.review_quiz, name='review-quiz'),
    path('quizzes', views.quizzes, name='quizzes'),
    
    # Post URLs
    path('post_cours',views.post_cours,name='post_cours'),
    path('delete_chapitre',views.delete_chapitre,name='delete_chapitre'),
    path('delete_lesson',views.delete_lesson,name='delete_lesson'),
    path('post_lesson',views.post_lesson,name='post_lesson'),
    path('update_profil', views.update_profil, name='update_profil'),
    path('update_password', views.update_password, name='update_password'),
    path('post_forum', views.post_forum, name='post_forum'),
]