from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

from .models import Classes, Subjects, Students, Teachers

User = get_user_model()




class GetAllSubjectsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_all_subjects_url = reverse('school:get_all_subjects')
        
        self.subject1 = Subjects.objects.create(name='Mathématiques')
        self.subject2 = Subjects.objects.create(name='Français')
        self.subject3 = Subjects.objects.create(name='Histoire')

    def test_get_all_subjects_success(self):
        response = self.client.get(self.get_all_subjects_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertEqual(len(response_data), 3)
        subject_names = [subject['name'] for subject in response_data]
        self.assertIn('Mathématiques', subject_names)
        self.assertIn('Français', subject_names)
        self.assertIn('Histoire', subject_names)


class GetClasseAllStudentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_classe_students_url = reverse('school:get_classe_all_students')
        self.classe = Classes.objects.create(name='6A')
        
        self.student_user1 = User.objects.create_user(
            email='student1@example.com',
            password='testpassword123',
            first_name='Jean',
            last_name='Dupont',
            is_student=True
        )
        
        self.student_user2 = User.objects.create_user(
            email='student2@example.com',
            password='testpassword123',
            first_name='Marie',
            last_name='Martin',
            is_student=True
        )
        
        self.student1 = Students.objects.create(user=self.student_user1, classe=self.classe)
        self.student2 = Students.objects.create(user=self.student_user2, classe=self.classe)

    def test_get_classe_all_students_success(self):
        response = self.client.post(
            self.get_classe_students_url,
            data=json.dumps('6A'),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertEqual(len(response_data), 2)
        self.assertIn(str(self.student1.id), response_data)
        self.assertIn(str(self.student2.id), response_data)
        self.assertEqual(response_data[str(self.student1.id)]['first_name'], 'Jean')
        self.assertEqual(response_data[str(self.student1.id)]['last_name'], 'Dupont')
        self.assertEqual(response_data[str(self.student2.id)]['first_name'], 'Marie')
        self.assertEqual(response_data[str(self.student2.id)]['last_name'], 'Martin')

