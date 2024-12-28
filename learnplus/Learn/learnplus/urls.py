from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('school.urls')),  # URLs de base
    path('instructor/', include('instructor.urls')),  # URLs des instructeurs
    path('student/', include('student.urls')),  # URLs des étudiants
    path('quiz/', include('quiz.urls')),  # URLs des quiz
    path('forum/', include('forum.urls')),  # URLs du forum
    path('chat/', include('chat.urls')),  # URLs du chat
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Gestion des erreurs
handler404 = 'school.views.handler404'
handler500 = 'school.views.handler500'
