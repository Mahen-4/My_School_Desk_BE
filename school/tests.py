from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

from .models import Classes, Subjects, Students, Teachers

User = get_user_model()

class GetAllClassesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_all_classes_url = reverse('school:get_all_classes')
        self.classe1 = Classes.objects.create(name='6A')
        self.classe2 = Classes.objects.create(name='5B')
        self.classe3 = Classes.objects.create(name='4C')

    def test_get_all_classes_success(self):
        response = self.client.get(self.get_all_classes_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 3)
        class_names = [classe['name'] for classe in response_data]
        self.assertIn('6A', class_names)
        self.assertIn('5B', class_names)
        self.assertIn('4C', class_names)



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

    

class ClassesModelTestCase(TestCase):
    def setUp(self):
        self.classe = Classes.objects.create(name='6A')
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jean',
            last_name='Dupont',
            is_student=True
        )
        
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)

    def test_get_classe_students(self):
        students_data = self.classe.get_classe_students()
        
        self.assertEqual(len(students_data), 1)
        self.assertIn(self.student.id, students_data)
        self.assertEqual(students_data[self.student.id]['first_name'], 'Jean')
        self.assertEqual(students_data[self.student.id]['last_name'], 'Dupont')

    def test_classe_str_method(self):
        self.assertEqual(str(self.classe), '6A')

    def test_get_classe_homeworks_empty(self):
        homeworks = self.classe.get_classe_homeworks()
        self.assertEqual(len(homeworks), 0)

    def test_get_classe_last_homeworks_empty(self):
        last_homeworks = self.classe.get_classe_last_homeworks()
        self.assertEqual(len(last_homeworks), 0)

    def test_get_classe_quiz_empty(self):
        quiz = self.classe.get_classe_quiz()
        self.assertEqual(len(quiz), 0)


class StudentsModelTestCase(TestCase):
    def setUp(self):
        self.classe = Classes.objects.create(name='6A')
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jean',
            last_name='Dupont',
            is_student=True
        )
        
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)

    def test_student_str_method(self):
        expected_str = 'DUPONT Jean - 6A'
        self.assertEqual(str(self.student), expected_str)

    def test_get_results_by_subject_empty(self):
        results = self.student.get_results_by_subject()
        self.assertEqual(len(results), 0)

    def test_get_last_results_empty(self):
        results = self.student.get_last_results()
        self.assertEqual(len(results), 0)


class SubjectsModelTestCase(TestCase):
    def setUp(self):
        self.subject = Subjects.objects.create(name='Mathématiques')

    def test_subject_str_method(self):
        self.assertEqual(str(self.subject), 'Mathématiques')


class TeachersModelTestCase(TestCase):
    def setUp(self):
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='Pierre',
            last_name='Professeur',
            is_teacher=True
        )
        
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)

    def test_teacher_str_method(self):
        expected_str = 'PROFESSEUR Pierre - Mathématiques'
        self.assertEqual(str(self.teacher), expected_str)

    def test_get_homeworks_created_empty(self):
        homeworks = self.teacher.get_homeworks_created()
        self.assertEqual(len(homeworks), 0)

    def test_get_last_homeworks_created_empty(self):
        last_homeworks = self.teacher.get_last_homeworks_created()
        self.assertEqual(len(last_homeworks), 0)

    def test_get_results_created_empty(self):
        results = self.teacher.get_results_created()
        self.assertEqual(len(results), 0)

    def test_get_quiz_created_empty(self):
        quiz = self.teacher.get_quiz_created()
        self.assertEqual(len(quiz), 0)