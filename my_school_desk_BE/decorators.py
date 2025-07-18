# myapp/decorators.py
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def student_required(allow_admin=True):

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # check if student
            if hasattr(user, 'is_student') and user.is_student:
                return view_func(request, *args, **kwargs)
            
            #check if admin if allowed
            if allow_admin and (user.is_staff or user.is_superuser):
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("Accès réservé aux étudiants")
        
        return wrapper
    return decorator

def teacher_required(allow_admin=True):

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if hasattr(user, 'is_teacher') and user.is_teacher:
                return view_func(request, *args, **kwargs)
            
            if allow_admin and (user.is_staff or user.is_superuser):
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("Accès réservé aux enseignants")
        
        return wrapper
    return decorator

