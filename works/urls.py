from django.urls import path, include
from . import views

urlpatterns = [
    path('all_created_teacher', views.get_all_homeworks_created_teacher, name="get_all_homeworks_created_teacher"),
    path('add_homework', views.add_homework, name="add_homework"),
    path('edit_homework', views.edit_homework, name="edit_homework"),
    path('delete_homework/<int:id>', views.delete_homework, name="delete_homework"),
    path('all', views.get_all_homeworks, name="get_all_homeworks"),
    path('get_last_homeworks', views.get_last_homeworks, name="get_last_homeworks"),
    path('get_last_homeworks_created_teacher', views.get_last_homeworks_created_teacher, name="get_last_homeworks_created_teacher"),
]