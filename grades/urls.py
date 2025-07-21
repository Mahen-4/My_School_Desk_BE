from django.urls import path, include
from . import views

urlpatterns = [
    path('add', views.add_results, name="add_results"),
    path('get_created', views.get_created, name="get_created"),
    path('edit', views.edit_result, name="edit_result"),
    path('delete/<str:title_classe>', views.delete_results, name="delete_results"),
    path('get_student_results', views.get_student_results, name="get_student_results"),
    path('get_last_results', views.get_last_results, name="get_last_results")
]