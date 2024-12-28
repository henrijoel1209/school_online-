from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class QueryCacheMiddleware(MiddlewareMixin):
    """Middleware pour la mise en cache des requêtes fréquentes"""
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
            
        # Cache des cours pour les étudiants
        if hasattr(request.user, 'student_user'):
            cache_key = f'student_courses_{request.user.id}'
            cached_courses = cache.get(cache_key)
            if cached_courses is None:
                from school.models import Cours
                cached_courses = list(Cours.objects.filter(
                    chapitre__classe=request.user.student_user.classe,
                    status=True
                ).values('id', 'titre', 'description'))
                cache.set(cache_key, cached_courses, 300)  # Cache pour 5 minutes
            request.cached_courses = cached_courses
            
        # Cache des matières pour les enseignants
        if hasattr(request.user, 'instructor'):
            cache_key = f'instructor_matieres_{request.user.id}'
            cached_matieres = cache.get(cache_key)
            if cached_matieres is None:
                cached_matieres = list(request.user.instructor.matieres.all().values('id', 'nom'))
                cache.set(cache_key, cached_matieres, 300)
            request.cached_matieres = cached_matieres
