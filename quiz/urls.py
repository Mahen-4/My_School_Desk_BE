from django.urls import path, include
from . import views

urlpatterns = [
    path('quiz/add', views.add_quiz),
    path('quiz/get_teacher_created_quiz', views.get_teacher_created_quiz),
    path('quiz/get_quiz_info', views.get_quiz_info),
    path('quiz/edit', views.edit_quiz),
    path('quiz/delete_question/<int:id>', views.delete_question),
    path('quiz/delete_quiz/<int:id>', views.delete_quiz),
    
]