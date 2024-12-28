from django.contrib import admin
from .models import Sujet, Reponse

# Register your models here.

@admin.register(Sujet)
class SujetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'user', 'cours', 'date_add', 'status')
    list_filter = ('status', 'date_add', 'cours')
    search_fields = ('titre', 'question', 'user__username')
    ordering = ('-date_add',)
    readonly_fields = ('slug',)

@admin.register(Reponse)
class ReponseAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'user', 'date_add', 'status')
    list_filter = ('status', 'date_add')
    search_fields = ('reponse', 'user__username', 'sujet__titre')
    ordering = ('-date_add',)
    readonly_fields = ('slug',)
