from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, StudentResponse, Assignment, AssignmentSubmission
from django.utils.safestring import mark_safe
from actions.action import Action

# Register your models here.

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3

@admin.register(Question)
class QuestionAdmin(Action):
    list_display = ('texte', 'quiz', 'question_type', 'points', 'status','date_add')
    list_filter = ('quiz', 'question_type', 'status','date_add')
    search_fields = ('texte',)
    inlines = [AnswerInline]
    date_hierarchy = 'date_add'
    list_display_links = ['texte']
    ordering = ['texte']
    list_per_page = 10
    fieldsets = [('Info Question',{'fields':['quiz','texte','question_type','points']}),
                ('Status et Activations',{'fields':['status']})
               ]

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(Action):
    list_display = ('titre', 'cours', 'date_debut', 'date_fin', 'duree', 'tentatives_max', 'status','date_add')
    list_filter = ('cours', 'status','date_add')
    search_fields = ('titre', 'description')
    inlines = [QuestionInline]
    date_hierarchy = 'date_add'
    list_display_links = ['titre']
    ordering = ['titre']
    list_per_page = 10
    fieldsets = [('Info Quiz',{'fields':['titre','description','cours','duree','tentatives_max','note_minimale']}),
                ('Status et Activations',{'fields':['status','date_debut','date_fin']})
               ]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(Action):
    list_display = ('student', 'quiz', 'score', 'started_at', 'completed_at', 'status')
    list_filter = ('quiz', 'student', 'status')
    search_fields = ('student__username', 'quiz__titre')
    readonly_fields = ('started_at',)
    date_hierarchy = 'started_at'
    list_display_links = ['student']
    ordering = ['-started_at']
    list_per_page = 10
    fieldsets = [('Info Tentative',{'fields':['quiz','student','score','completed_at']}),
                ('Status',{'fields':['status']})
               ]

@admin.register(StudentResponse)
class StudentResponseAdmin(Action):
    list_display = ('attempt', 'question', 'is_correct', 'date_add')
    list_filter = ('is_correct', 'question__quiz','date_add')
    search_fields = ('attempt__student__username', 'question__texte')
    readonly_fields = ('date_add',)
    date_hierarchy = 'date_add'
    list_display_links = ['attempt']
    ordering = ['-date_add']
    list_per_page = 10
    fieldsets = [('Info Réponse',{'fields':['attempt','question','selected_answers','text_response','is_correct']}),
                ('Status',{'fields':['status']})
               ]

@admin.register(Assignment)
class AssignmentAdmin(Action):
    list_display = ('titre', 'cours', 'date_debut', 'date_limite', 'points_max', 'status','date_add')
    list_filter = ('cours', 'status','date_add')
    search_fields = ('titre', 'description')
    date_hierarchy = 'date_add'
    list_display_links = ['titre']
    ordering = ['titre']
    list_per_page = 10
    fieldsets = [('Info Devoir',{'fields':['titre','description','cours','points_max','fichier_instruction']}),
                ('Dates',{'fields':['date_debut','date_limite']}),
                ('Status',{'fields':['status']})
               ]

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(Action):
    list_display = ('student', 'assignment', 'note', 'submitted_at', 'is_late', 'status')
    list_filter = ('assignment', 'status')
    search_fields = ('student__username', 'assignment__titre')
    readonly_fields = ('submitted_at', 'is_late')
    date_hierarchy = 'submitted_at'
    list_display_links = ['student']
    ordering = ['-submitted_at']
    list_per_page = 10
    fieldsets = [('Info Soumission',{'fields':['assignment','student','fichier_reponse','commentaire']}),
                ('Évaluation',{'fields':['note','feedback']}),
                ('Status',{'fields':['status']})
               ]
