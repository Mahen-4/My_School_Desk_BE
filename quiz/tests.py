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


class EditQuizTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.edit_quiz_url = reverse('quiz:edit_quiz')
        
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
        
        self.quiz = Quiz.objects.create(
            title='Quiz Original',
            description='Description originale',
            teacher=self.teacher
        )
        self.question = Questions.objects.create(
            title='Question originale',
            quiz=self.quiz
        )
        self.response = Responses.objects.create(
            title='Réponse originale',
            is_answer=True,
            question=self.question
        )

    def test_edit_quiz_success(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'quiz_id': self.quiz.id,
            'title': 'Quiz Modifié',
            'description': 'Description modifiée',
            'classes': ['6A'],
            'questions_responses': {
                'Question modifiée': [
                    {
                        'question_id': self.question.id,
                        'response_id': self.response.id,
                        'response_title': 'Réponse modifiée',
                        'is_answer': False
                    }
                ]
            }
        }
        
        response = self.client.put(
            self.edit_quiz_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        updated_quiz = Quiz.objects.get(id=self.quiz.id)
        self.assertEqual(updated_quiz.title, 'Quiz Modifié')
        self.assertEqual(updated_quiz.description, 'Description modifiée')

    def test_edit_quiz_not_found(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'quiz_id': 999,
            'title': 'Quiz Modifié',
            'description': 'Description modifiée',
            'classes': ['6A'],
            'questions_responses': {}
        }
        
        response = self.client.put(
            self.edit_quiz_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'Erreur lors de la modification du quiz')


class DeleteQuizTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
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
            title='Quiz à supprimer',
            description='Description',
            teacher=self.teacher
        )

    def test_delete_quiz_success(self):
        self.client.force_login(self.teacher_user)
        
        delete_url = reverse('quiz:delete_quiz', kwargs={'id': self.quiz.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Quiz supprimé !')
        
        with self.assertRaises(Quiz.DoesNotExist):
            Quiz.objects.get(id=self.quiz.id)

    def test_delete_quiz_not_found(self):
        self.client.force_login(self.teacher_user)
        delete_url = reverse('quiz:delete_quiz', kwargs={'id': 999})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "Le Quiz n'a pas été supprimé !")


class AddAttemptTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.add_attempt_url = reverse('quiz:add_attempt')
        
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.classe = Classes.objects.create(name='6A')
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        self.quiz = Quiz.objects.create(
            title='Quiz Test',
            description='Description',
            teacher=self.teacher
        )

    def test_add_attempt_new_success(self):
        self.client.force_login(self.student_user)
        
        data = {
            'quiz_id': self.quiz.id,
            'score': '8/10'
        }
        response = self.client.post(
            self.add_attempt_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Insertion réussie')
        attempt = Attempts.objects.get(student=self.student, quiz=self.quiz)
        self.assertEqual(attempt.score, '8/10')

    def test_add_attempt_update_existing(self):
        self.client.force_login(self.student_user)
        
        existing_attempt = Attempts.objects.create(
            student=self.student,
            quiz=self.quiz,
            score='5/10'
        )
        
        data = {
            'quiz_id': self.quiz.id,
            'score': '9/10'
        }
        
        response = self.client.post(
            self.add_attempt_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Mise à jour réussie')
        updated_attempt = Attempts.objects.get(id=existing_attempt.id)
        self.assertEqual(updated_attempt.score, '9/10')


class GetQuizInfoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_quiz_info_url = reverse('quiz:get_quiz_info')
        
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.classe = Classes.objects.create(name='6A')
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        
        self.quiz = Quiz.objects.create(
            title='Quiz Test',
            description='Description test',
            teacher=self.teacher
        )

    def test_get_quiz_info_without_attempt(self):
        self.client.force_login(self.student_user)
        
        response = self.client.post(
            self.get_quiz_info_url,
            data=json.dumps(self.quiz.id),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn(str(self.quiz.id), response_data)
        self.assertEqual(response_data[str(self.quiz.id)]['quiz_title'], 'Quiz Test')

    def test_get_quiz_info_with_attempt(self):
        self.client.force_login(self.student_user)
        
        attempt = Attempts.objects.create(
            student=self.student,
            quiz=self.quiz,
            score='7/10'
        )
        
        response = self.client.post(
            self.get_quiz_info_url,
            data=json.dumps(self.quiz.id),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['last_score'], '7/10')
        self.assertIn('date_last_attempt', response_data)

    def test_get_quiz_info_not_found(self):
        self.client.force_login(self.student_user)
        
        response = self.client.post(
            self.get_quiz_info_url,
            data=json.dumps(999),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'Quiz introuvable ')


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


class GetClasseQuizTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_classe_quiz_url = reverse('quiz:get_classe_quiz')
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        
        self.classe = Classes.objects.create(name='6A')
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)

    def test_get_classe_quiz_success(self):
        self.client.force_login(self.student_user)
    
        response = self.client.get(self.get_classe_quiz_url)
        
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


class DeleteQuestionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
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
        
        self.question = Questions.objects.create(
            title='Question test',
            quiz=self.quiz
        )

    def test_delete_question_success(self):
        self.client.force_login(self.teacher_user)
        delete_url = reverse('quiz:delete_question', kwargs={'id': self.question.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Question supprimée !')
        
        with self.assertRaises(Questions.DoesNotExist):
            Questions.objects.get(id=self.question.id)

    def test_delete_question_not_found(self):
        self.client.force_login(self.teacher_user)
        delete_url = reverse('quiz:delete_question', kwargs={'id': 999})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "La question n'a pas été supprimée !")