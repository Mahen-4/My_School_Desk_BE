from django.urls import path, include
from . import views

urlpatterns = [
    path('results/add', views.add_results, name="add_results"),
    path('results/get_created', views.get_created, name="get_created"),
    path('results/edit', views.edit_result, name="edit_result"),
    path('results/delete/<str:title_classe>', views.delete_results, name="delete_results"),
    path('results/get_student_results', views.get_student_results, name="get_student_results"),
    path('results/get_last_results', views.get_last_results, name="get_last_results")
]