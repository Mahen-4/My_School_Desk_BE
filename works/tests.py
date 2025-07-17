from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import datetime

from school.models import Classes, Students, Teachers, Subjects
from .models import HomeWorks

User = get_user_model()

class AddHomeworkTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.add_homework_url = reverse('works:add_homework')
        
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

    def test_add_homework_success(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'description': 'Exercices page 45',
            'due_date': '2025-01-30',
            'classe': '6A'
        }
        
        response = self.client.post(
            self.add_homework_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Devoir ajouté !')
        
        homework = HomeWorks.objects.get(description='Exercices page 45')
        self.assertEqual(homework.classe, self.classe)
        self.assertEqual(homework.teacher, self.teacher)
        self.assertEqual(homework.due_date, datetime.date(2025, 1, 30))

    def test_add_homework_invalid_class(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'description': 'Exercices page 45',
            'due_date': '2025-01-30',
            'classe': 'ClasseInexistante'
        }
        
        response = self.client.post(
            self.add_homework_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "Erreur lors de l'ajout !")

    


class EditHomeworkTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.edit_homework_url = reverse('works:edit_homework')
        
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
        self.classe2 = Classes.objects.create(name='5B')
        
        self.homework = HomeWorks.objects.create(
            description='Description originale',
            due_date=datetime.date(2025, 1, 30),
            classe=self.classe,
            teacher=self.teacher
        )

    def test_edit_homework_success(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'homework_id': self.homework.id,
            'description': 'Description modifiée',
            'due_date': '2025-02-15',
            'classe': '5B'
        }
        
        response = self.client.put(
            self.edit_homework_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'devoir modifié !')
        updated_homework = HomeWorks.objects.get(id=self.homework.id)
        self.assertEqual(updated_homework.description, 'Description modifiée')
        self.assertEqual(updated_homework.due_date, datetime.date(2025, 2, 15))
        self.assertEqual(updated_homework.classe, self.classe2)        

    


class DeleteHomeworkTestCase(TestCase):
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
        self.classe = Classes.objects.create(name='6A')
        
        self.homework = HomeWorks.objects.create(
            description='Devoir à supprimer',
            due_date=datetime.date(2025, 1, 30),
            classe=self.classe,
            teacher=self.teacher
        )

    def test_delete_homework_success(self):
        self.client.force_login(self.teacher_user)
        
        delete_url = reverse('works:delete_homework', kwargs={'id': self.homework.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Devoirs supprimé !')
        
        with self.assertRaises(HomeWorks.DoesNotExist):
            HomeWorks.objects.get(id=self.homework.id)

    


class GetHomeworksTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_all_homeworks_url = reverse('works:get_all_homeworks')
        self.get_all_homeworks_created_url = reverse('works:get_all_homeworks_created_teacher')
        self.subject = Subjects.objects.create(name='Mathématiques')
        self.classe = Classes.objects.create(name='6A')
        
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
        
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        
        self.homework = HomeWorks.objects.create(
            description='Exercices page 45',
            due_date=datetime.date(2025, 1, 30),
            classe=self.classe,
            teacher=self.teacher
        )

    def test_get_all_homeworks_student(self):
        self.client.force_login(self.student_user)
        
        response = self.client.get(self.get_all_homeworks_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn(str(self.homework.id), response_data)
        homework_data = response_data[str(self.homework.id)]
        self.assertEqual(homework_data['homework_subject'], 'Mathématiques')
        self.assertEqual(homework_data['homework_description'], 'Exercices page 45')

    def test_get_all_homeworks_created_teacher(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(self.get_all_homeworks_created_url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertIsInstance(response_data, dict)
        self.assertIn(str(self.homework.id), response_data)
        homework_data = response_data[str(self.homework.id)]
        self.assertEqual(homework_data['homework_description'], 'Exercices page 45')
        self.assertEqual(homework_data['classe_name'], '6A')
        self.assertIn('homework_created_at', homework_data)
        self.assertEqual(homework_data['homework_due_date'], '30-01-2025')


class GetLastHomeworksTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_last_homeworks_url = reverse('works:get_last_homeworks')
        self.get_last_homeworks_created_url = reverse('works:get_last_homeworks_created_teacher')
        
        self.subject = Subjects.objects.create(name='Mathématiques')
        self.classe = Classes.objects.create(name='6A')
        
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
        
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)

    def test_get_last_homeworks_student(self):
        self.client.force_login(self.student_user)
        
        response = self.client.get(self.get_last_homeworks_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, list)

    def test_get_last_homeworks_created_teacher(self):
        self.client.force_login(self.teacher_user)
        
        response = self.client.get(self.get_last_homeworks_created_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, list)


class HomeWorksModelTestCase(TestCase):
    def setUp(self):
        self.subject = Subjects.objects.create(name='Mathématiques')
        self.classe = Classes.objects.create(name='6A')
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)

    def test_create_homework_success(self):
        homework = HomeWorks.objects.create(
            description='Exercices page 45',
            due_date=datetime.date(2025, 1, 30),
            classe=self.classe,
            teacher=self.teacher
        )
        
        self.assertEqual(homework.description, 'Exercices page 45')
        self.assertEqual(homework.due_date, datetime.date(2025, 1, 30))
        self.assertEqual(homework.classe, self.classe)
        self.assertEqual(homework.teacher, self.teacher)
        self.assertIsNotNone(homework.created_at)

    def test_homework_cascade_delete_classe(self):
        homework = HomeWorks.objects.create(
            description='Exercices page 45',
            due_date=datetime.date(2025, 1, 30),
            classe=self.classe,
            teacher=self.teacher
        )
        
        self.classe.delete()
        with self.assertRaises(HomeWorks.DoesNotExist):
            HomeWorks.objects.get(id=homework.id)

    def test_homework_cascade_delete_teacher(self):
        homework = HomeWorks.objects.create(
            description='Exercices page 45',
            due_date=datetime.date(2025, 1, 30),
            classe=self.classe,
            teacher=self.teacher
        )
        
        self.teacher.delete()
        
        with self.assertRaises(HomeWorks.DoesNotExist):
            HomeWorks.objects.get(id=homework.id)