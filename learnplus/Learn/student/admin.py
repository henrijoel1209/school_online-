from django.contrib import admin
from . import models
from django.utils.safestring import mark_safe

# Register your models here.
class CustomAdmin(admin.ModelAdmin):
    actions = ('activate','desactivate')
    list_filter = ('status',)
    list_per_page = 10
    date_hierachy = "date_add"

    def activate(self,request,queryset):
        queryset.update(status=True)
        self.message_user(request,'la selection a été effectué avec succes')
    activate.short_description = "permet d'activer le champs selectionner"

    def desactivate(self,request,queryset):  
        queryset.update(status=False)
        self.message_user(request,'la selection a été effectué avec succes')
    desactivate.short_description = "permet de desactiver le champs selectionner"

class StudentAdmin(CustomAdmin):
    list_display = ('user','classe','image_view','status')
    list_display_links = ['user',]
    search_fields = ('user',)
    ordering = ('user',)
    fieldsets = [
                 ("info éléve",{"fields":["user","classe","photo"]}),
                 ("standard",{"fields":["status"]})
    ]
    def image_view(self,obj):
        return mark_safe("<img src ='{url}' width='100px',height='50px'>".format(url=obj.photo.url))

class StudentResponseAdmin(CustomAdmin):
    list_display = ('student','status')
    list_display_links = ['student',]
    search_fields = ('student',)
    ordering = ('student',)
    fieldsets = [
                 ("info éléve reponse",{"fields":["student","question","reponse"]}),
                 ("standard",{"fields":["status"]})
    ]

def _register(model,admin_class):
    admin.site.register(model,admin_class)


_register(models.Student, StudentAdmin)
_register(models.StudentResponse, StudentResponseAdmin)



