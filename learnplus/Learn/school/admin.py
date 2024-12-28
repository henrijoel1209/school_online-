from django.contrib import admin
from . import models
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class CustomAdmin(admin.ModelAdmin):
    actions = ('activate', 'deactivate')
    list_filter = ('status',)
    list_per_page = 10
    date_hierarchy = "date_add"

    def activate(self, request, queryset):
        queryset.update(status=True)
        self.message_user(request, 'La sélection a été activée avec succès')
    activate.short_description = "Activer les éléments sélectionnés"

    def deactivate(self, request, queryset):  
        queryset.update(status=False)
        self.message_user(request, 'La sélection a été désactivée avec succès')
    deactivate.short_description = "Désactiver les éléments sélectionnés"

class MatiereAdmin(CustomAdmin):
    list_display = ('nom', 'image_preview', 'status', 'date_add', 'date_update')
    list_display_links = ['nom']
    search_fields = ('nom', 'description')
    ordering = ('nom',)
    readonly_fields = ('image_preview',)
    fieldsets = [
        ("Informations", {
            "fields": ["nom", "image", "image_preview", "description"]
        }),
        ("Paramètres", {
            "fields": ["status"]
        })
    ]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu'

class NiveauAdmin(CustomAdmin):
    list_display = ('nom', 'classes_count', 'status', 'date_add', 'date_update')
    list_display_links = ['nom']
    search_fields = ('nom',)
    ordering = ('nom',)
    fieldsets = [
        ("Informations", {
            "fields": ["nom"]
        }),
        ("Paramètres", {
            "fields": ["status"]
        })
    ]

    def classes_count(self, obj):
        return obj.classe_niveau.count()
    classes_count.short_description = 'Nombre de classes'

class ClasseAdmin(CustomAdmin):
    list_display = ('__str__', 'niveau', 'filiere', 'students_count', 'status')
    list_display_links = ['__str__']
    list_filter = ('niveau', 'filiere', 'status')
    search_fields = ('niveau__nom', 'filiere__nom')
    ordering = ('niveau', 'numeroClasse')
    fieldsets = [
        ("Informations", {
            "fields": ["niveau", "numeroClasse", "filiere"]
        }),
        ("Paramètres", {
            "fields": ["status"]
        })
    ]

    def students_count(self, obj):
        return obj.get_students().count()
    students_count.short_description = 'Nombre d\'étudiants'

class ChapitreAdmin(CustomAdmin):
    list_display = ('titre', 'matiere', 'classe', 'duree_en_heure', 'date_debut', 'date_fin', 'cours_count', 'status')
    list_display_links = ['titre']
    list_filter = ('matiere', 'classe', 'status')
    search_fields = ('titre', 'description', 'matiere__nom', 'classe__niveau__nom')
    ordering = ('date_debut', 'titre')
    readonly_fields = ('image_preview', 'video_preview')
    fieldsets = [
        ("Informations", {
            "fields": ["titre", "description", "matiere", "classe"]
        }),
        ("Médias", {
            "fields": ["image", "image_preview", "video", "video_preview"]
        }),
        ("Planning", {
            "fields": ["duree_en_heure", "date_debut", "date_fin"]
        }),
        ("Paramètres", {
            "fields": ["status"]
        })
    ]

    def cours_count(self, obj):
        return obj.get_cours().count()
    cours_count.short_description = 'Nombre de cours'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu de l\'image'

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="320" height="240" controls>'
                '<source src="{}" type="video/mp4">'
                'Votre navigateur ne supporte pas la lecture de vidéos.'
                '</video>', 
                obj.video.url
            )
        return "Aucune vidéo"
    video_preview.short_description = 'Aperçu de la vidéo'

class CoursAdmin(CustomAdmin):
    list_display = ('titre', 'chapitre', 'content_count', 'completion_rate', 'status')
    list_display_links = ['titre']
    list_filter = ('chapitre__matiere', 'chapitre__classe', 'status')
    search_fields = ('titre', 'description', 'chapitre__titre')
    ordering = ('chapitre', 'titre')
    readonly_fields = ('image_preview', 'video_preview', 'pdf_preview')
    fieldsets = [
        ("Informations", {
            "fields": ["titre", "description", "chapitre"]
        }),
        ("Médias", {
            "fields": [
                "image", "image_preview",
                "video", "video_preview",
                "pdf", "pdf_preview"
            ]
        }),
        ("Paramètres", {
            "fields": ["status"]
        })
    ]

    def content_count(self, obj):
        return obj.get_contents().count()
    content_count.short_description = 'Nombre de contenus'

    def completion_rate(self, obj):
        return f"{obj.get_completion_rate():.1f}%"
    completion_rate.short_description = 'Taux de complétion'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu de l\'image'

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="320" height="240" controls>'
                '<source src="{}" type="video/mp4">'
                'Votre navigateur ne supporte pas la lecture de vidéos.'
                '</video>', 
                obj.video.url
            )
        return "Aucune vidéo"
    video_preview.short_description = 'Aperçu de la vidéo'

    def pdf_preview(self, obj):
        if obj.pdf:
            return format_html('<a href="{}" target="_blank">Voir le PDF</a>', obj.pdf.url)
        return "Aucun PDF"
    pdf_preview.short_description = 'Aperçu du PDF'

class CourseContentAdmin(CustomAdmin):
    list_display = ('title', 'cours', 'content_type', 'order', 'status')
    list_display_links = ['title']
    list_filter = ('content_type', 'cours__chapitre__matiere', 'status')
    search_fields = ('title', 'text_content', 'cours__titre')
    ordering = ('cours', 'order')
    readonly_fields = ('file_preview',)
    fieldsets = [
        ("Informations", {
            "fields": ["title", "cours", "content_type", "order"]
        }),
        ("Contenu", {
            "fields": ["text_content", "file_content", "file_preview", "video_url"]
        }),
        ("Paramètres", {
            "fields": ["status"]
        })
    ]

    def file_preview(self, obj):
        if obj.file_content:
            if obj.content_type == 'image':
                return format_html('<img src="{}" style="max-height: 100px;"/>', obj.file_content.url)
            elif obj.content_type == 'pdf':
                return format_html('<a href="{}" target="_blank">Voir le PDF</a>', obj.file_content.url)
        return "Aucun fichier"
    file_preview.short_description = 'Aperçu du fichier'

# Enregistrement des modèles
admin.site.register(models.Matiere, MatiereAdmin)
admin.site.register(models.Niveau, NiveauAdmin)
admin.site.register(models.Classe, ClasseAdmin)
admin.site.register(models.Chapitre, ChapitreAdmin)
admin.site.register(models.Cours, CoursAdmin)
admin.site.register(models.CourseContent, CourseContentAdmin)
