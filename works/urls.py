from django.urls import path, include
from . import views

urlpatterns = [
    path('homeworks/all_created_teacher', views.get_all_homeworks_created_teacher, name="get_all_homeworks_created_teacher"),
    path('homeworks/add_homework', views.add_homework, name="add_homework"),
    path('homeworks/edit_homework', views.edit_homework, name="edit_homework"),
    path('homeworks/delete_homework/<int:id>', views.delete_homework, name="delete_homework"),
    path('homeworks/all', views.get_all_homeworks, name="get_all_homeworks"),
    path('homeworks/get_last_homeworks', views.get_last_homeworks, name="get_last_homeworks"),
    path('homeworks/get_last_homeworks_created_teacher', views.get_last_homeworks_created_teacher, name="get_last_homeworks_created_teacher"),
]