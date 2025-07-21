from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
import json

from school.models import Classes, Students, Teachers, Subjects
from .models import Quiz, Questions, Responses, Attempts

User = get_user_model()

class AddQuizTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.add_quiz_url = reverse('quiz:add_quiz')
        
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        self.classe = Classes.objects.create(name='6A')

    def test_add_quiz_success(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'title': 'Quiz Math',
            'description': 'Test de mathématiques',
            'classes': ['6A'],
            'questions_responses': {
                'Question 1': [
                    {'text': 'Réponse A', 'is_answer': True},
                    {'text': 'Réponse B', 'is_answer': False}
                ],
                'Question 2': [
                    {'text': 'Réponse C', 'is_answer': False},
                    {'text': 'Réponse D', 'is_answer': True}
                ]
            }
        }
        
        response = self.client.post(
            self.add_quiz_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'quiz ajouté')
        quiz = Quiz.objects.get(title='Quiz Math')
        self.assertEqual(quiz.description, 'Test de mathématiques')
        self.assertEqual(quiz.quiz_questions.count(), 2)

    def test_add_quiz_invalid_class(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'title': 'Quiz Math',
            'description': 'Test de mathématiques',
            'classes': ['ClasseInexistante'],
            'questions_responses': {}
        }
        response = self.client.post(
            self.add_quiz_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'Classe invalide')





class GetTeacherCreatedQuizTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_teacher_created_quiz_url = reverse('quiz:get_teacher_created_quiz')
        
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)

    def test_get_teacher_created_quiz_success(self):
        self.client.force_login(self.teacher_user)
    
        response = self.client.get(self.get_teacher_created_quiz_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})






class QuizModelTestCase(TestCase):
    def setUp(self):
        self.subject = Subjects.objects.create(name='Mathématiques')
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        
        self.quiz = Quiz.objects.create(
            title='Quiz Test',
            description='Description test',
            teacher=self.teacher
        )

    def test_get_questions_responses(self):
        question = Questions.objects.create(
            title='Question test',
            quiz=self.quiz
        )
        
        response1 = Responses.objects.create(
            title='Réponse 1',
            is_answer=True,
            question=question
        )
        
        response2 = Responses.objects.create(
            title='Réponse 2',
            is_answer=False,
            question=question
        )
        
        questions_responses = self.quiz.get_questions_responses()
        self.assertIn('Question test', questions_responses)
        self.assertEqual(len(questions_responses['Question test']), 2)
        self.assertEqual(questions_responses['Question test'][0]['response_title'], 'Réponse 1')
        self.assertTrue(questions_responses['Question test'][0]['is_answer'])

    def test_get_quiz_info(self):
        quiz_info = self.quiz.get_quiz_info()
        self.assertIn(self.quiz.id, quiz_info)
        self.assertEqual(quiz_info[self.quiz.id]['quiz_title'], 'Quiz Test')
        self.assertEqual(quiz_info[self.quiz.id]['quiz_description'], 'Description test')
        self.assertIn('quiz_added_date', quiz_info[self.quiz.id])

