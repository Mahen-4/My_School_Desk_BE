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

    def test_login_missing_email(self):
        data = {
            'password': 'testpassword123'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)

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

    def test_login_2fa_code_expiration(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        expire_key = f"digi_code_expire{self.test_user.email}"
        self.assertIn(expire_key, self.client.session)
        expire_time = datetime.datetime.fromisoformat(self.client.session[expire_key])
        now = datetime.datetime.now()
        time_diff = expire_time - now
        
        self.assertAlmostEqual(time_diff.total_seconds(), 300, delta=10)


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

    def test_user_data_unauthenticated(self):
        response = self.client.get(self.user_data_url)
        self.assertIn(response.status_code, [302, 401])

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

    def test_user_data_regular_user(self): 
        regular_user = User.objects.create_user(
            email='regular@example.com',
            password='testpassword123',
            first_name='Regular',
            last_name='User'
        )
        
        self.client.force_login(regular_user)
        response = self.client.get(self.user_data_url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['email'], 'regular@example.com')
        self.assertEqual(response_data['first_name'], 'Regular')
        self.assertEqual(response_data['last_name'], 'User')
        self.assertFalse(response_data['is_student'])
        self.assertFalse(response_data['is_teacher'])


class UserModelTestCase(TestCase): 
    def test_create_user_success(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_missing_required_fields(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpassword123',
                first_name='John',
                last_name='Doe'
            )
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test@example.com',
                password='testpassword123',
                last_name='Doe'
            )

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123',
            first_name='Admin',
            last_name='User'
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_invalid_permissions(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpassword123',
                first_name='Admin',
                last_name='User',
                is_staff=False
            )

    def test_user_string_representation(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe',
            is_student=True
        )
        
        expected_str = 'test@example.com - DOE John - is student :  True - is teacher : False - is staff : False'
        self.assertEqual(str(user), expected_str)