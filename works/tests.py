from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import datetime
from datetime import timedelta
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



class TestGetHomeworksCreated(TestCase):
    def setUp(self):
        #create objects
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            is_teacher=True
        )
        self.teacher = Teachers.objects.create(user=self.teacher_user)
        self.classe = Classes.objects.create(name="6ème A")
        
    def test_get_homeworks_created_empty(self):
        result = self.teacher.get_homeworks_created()
        self.assertEqual(result, {})
        
    def test_get_homeworks_created_with_data(self):
        #test with homework
        due_date = datetime.now() + timedelta(days=7)
        homework = HomeWorks.objects.create(
            description="Exercices page 42",
            due_date=due_date,
            teacher=self.teacher,
            classe=self.classe
        )
        result = self.teacher.get_homeworks_created()
        
        #check count
        self.assertEqual(len(result), 1)
        self.assertIn(homework.id, result)

        #check values
        homework_data = result[homework.id]
        self.assertEqual(homework_data["homework_description"], "Exercices page 42")
        self.assertEqual(homework_data["homework_due_date"], due_date.strftime('%d-%m-%Y'))
        self.assertEqual(homework_data["classe_name"], "6ème A")