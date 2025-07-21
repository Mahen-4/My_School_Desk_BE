from django.urls import path, include
from . import views

urlpatterns = [
    path('add', views.add_quiz, name="add_quiz"),
    path('get_teacher_created_quiz', views.get_teacher_created_quiz, name="get_teacher_created_quiz"),
    path('get_quiz_questions_responses', views.get_quiz_questions_responses, name="get_quiz_questions_responses"),
    path('edit', views.edit_quiz, name="edit_quiz"),
    path('delete_question/<int:id>', views.delete_question, name="delete_question"),
    path('delete_quiz/<int:id>', views.delete_quiz, name="delete_quiz"),
    path('get_classe_quiz', views.get_classe_quiz, name="get_classe_quiz"),
    path('get_quiz_info', views.get_quiz_info, name="get_quiz_info"),
    path('add_attempt', views.add_attempt, name="add_attempt"),
    
]