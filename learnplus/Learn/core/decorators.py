from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect

def student_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'student_user'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

def instructor_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'instructor'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'admin_manager'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
