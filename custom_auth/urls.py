from django.urls import path, include
from . import views

urlpatterns = [
    path('csrf/', views.get_csrf),
    path('login/', views.logIn),
    path('digi_code_check/',views.digi_code_check),
]