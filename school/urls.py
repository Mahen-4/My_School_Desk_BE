from django.urls import path, include
from . import views

urlpatterns = [
    path('classes/all', views.get_all_classes),
    path('subjects/all', views.get_all_subjects),
    path('classes/all_students', views.get_classe_all_students),
]