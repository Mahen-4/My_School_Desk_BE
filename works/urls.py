from django.urls import path, include
from . import views

urlpatterns = [
    path('homeworks/all_created_teacher', views.get_all_homeworks_created_teacher),
    path('homeworks/add_homework', views.add_homework)
]