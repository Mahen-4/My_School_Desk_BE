from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse
from django.core import mail
from django.http import JsonResponse
from unittest.mock import patch, MagicMock
import json
import datetime
from datetime import timedelta

from .models import User
from school.models import Students, Teachers, Classes, Subjects

User = get_user_model()

class LogInTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('custom_auth:login')  
        
        self.test_user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )

    def test_login_success(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Authentification réussi')
        self.assertEqual(self.client.session['user_email'], 'test@example.com')
        self.assertIn(f"digi_code{self.test_user.email}", self.client.session)
        self.assertIn(f"digi_code_expire{self.test_user.email}", self.client.session)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "MySchoolDesk - Votre code d'authentification à deux facteurs (2FA)")
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])

    def test_login_invalid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'Utilisateur introuvable')

    def test_login_user_not_found(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'Utilisateur introuvable')

  

    def test_login_2fa_code_generation(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        digi_code_key = f"digi_code{self.test_user.email}"
        self.assertIn(digi_code_key, self.client.session)
        
        stored_code = self.client.session[digi_code_key]
        self.assertTrue(stored_code.startswith('pbkdf2_sha256'))

    

class UserDataTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data_url = reverse('custom_auth:user_data') 
        self.classe = Classes.objects.create(name='6A')
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
            first_name='Bob',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)

   
    def test_user_data_authenticated_student(self): 
        self.client.force_login(self.student_user)
        response = self.client.get(self.user_data_url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['email'], 'student@example.com')
        self.assertEqual(response_data['first_name'], 'Jane')
        self.assertEqual(response_data['last_name'], 'Student')
        self.assertTrue(response_data['is_student'])
        self.assertEqual(response_data['classe'], '6A')  

    def test_user_data_authenticated_teacher(self):
        self.client.force_login(self.teacher_user)
        
        response = self.client.get(self.user_data_url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['email'], 'teacher@example.com')
        self.assertEqual(response_data['first_name'], 'Bob')
        self.assertEqual(response_data['last_name'], 'Teacher')
        self.assertTrue(response_data['is_teacher'])
        self.assertEqual(response_data['subject'], 'Mathématiques')  

   

