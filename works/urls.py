from django.urls import path, include
from . import views

urlpatterns = [
    path('homeworks/all_created_teacher', views.get_all_homeworks_created_teacher),
    path('homeworks/add_homework', views.add_homework),
    path('homeworks/edit_homework', views.edit_homework),
    path('homeworks/delete_homework/<int:id>', views.delete_homework),
    path('homeworks/all', views.get_all_homeworks),
    path('homeworks/get_last_homeworks', views.get_last_homeworks),

]