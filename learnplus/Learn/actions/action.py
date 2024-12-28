from django.contrib import admin

class Action(admin.ModelAdmin):
    """Classe de base pour les actions d'administration"""
    actions = ('activate', 'deactivate')
    list_filter = ('status',)
    list_per_page = 10

    def activate(self, request, queryset):
        """Active les éléments sélectionnés"""
        queryset.update(status=True)
        self.message_user(request, 'Les éléments ont été activés avec succès')
    activate.short_description = "Activer les éléments sélectionnés"

    def deactivate(self, request, queryset):
        """Désactive les éléments sélectionnés"""
        queryset.update(status=False)
        self.message_user(request, 'Les éléments ont été désactivés avec succès')
    deactivate.short_description = "Désactiver les éléments sélectionnés"
