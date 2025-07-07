from django.urls import path, include
from . import views

urlpatterns = [
    path('csrf/', views.get_csrf),
    path('login/', views.login)
]