from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from school.models import Classes, Students, Teachers, Subjects
from .models import Results

User = get_user_model()

class AddResultsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.add_results_url = reverse('grades:add_results')  
        
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.classe = Classes.objects.create(name='6A')
        
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        
        self.student_user1 = User.objects.create_user(
            email='student1@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student1',
            is_student=True
        )
        
        self.student_user2 = User.objects.create_user(
            email='student2@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Student2',
            is_student=True
        )
        
        self.student1 = Students.objects.create(user=self.student_user1, classe=self.classe)
        self.student2 = Students.objects.create(user=self.student_user2, classe=self.classe)

    def test_add_results_success(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'title': 'Contrôle Math',
            'result_on': 20,
            'classe_name': '6A',
            'all_results': {
                str(self.student1.id): 15.5,  
                str(self.student2.id): 18.0
            }
        }
        
        response = self.client.post(
            self.add_results_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Résultats ajoutés')
        results = Results.objects.filter(title='Contrôle Math')
        self.assertEqual(results.count(), 2)

    def test_add_results_classe_not_found(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'title': 'Contrôle Math',
            'result_on': 20,
            'classe_name': 'ClasseInexistante',
            'all_results': {str(self.student1.id): 15.5}
        }
        
        response = self.client.post(
            self.add_results_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "Erreur d'ajout")

   


class EditResultTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.edit_result_url = reverse('grades:edit_result') 
        
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.classe = Classes.objects.create(name='6A')
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)
        
        self.result = Results.objects.create(
            title='Contrôle Math',
            score=15.5,
            score_on=20,
            classe=self.classe,
            student=self.student,
            teacher=self.teacher
        )

    def test_edit_result_success(self):
        self.client.force_login(self.teacher_user)
        
        data = {
            'title': 'Contrôle Math Modifié',
            'result_on': 25,
            'all_results': {
                str(self.result.id): 20.0
            }
        }
        
        response = self.client.put(
            self.edit_result_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'Résultat(s) modifié(s)')
        
        updated_result = Results.objects.get(id=self.result.id)
        self.assertEqual(updated_result.title, 'Contrôle Math Modifié')
        self.assertEqual(updated_result.score_on, 25)
        self.assertEqual(updated_result.score, 20.0)

    


class DeleteResultsTestCase(TestCase):
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
        
        self.classe = Classes.objects.create(name='6A')
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)
        
        self.result1 = Results.objects.create(
            title='Contrôle Math',
            score=15.5,
            score_on=20,
            classe=self.classe,
            student=self.student,
            teacher=self.teacher
        )
        
        self.result2 = Results.objects.create(
            title='Contrôle Math',
            score=18.0,
            score_on=20,
            classe=self.classe,
            student=self.student,
            teacher=self.teacher
        )

    def test_delete_results_success(self):
        self.client.force_login(self.teacher_user)
        
        title_classe = 'Contrôle Math-6A'
        delete_url = reverse('grades:delete_results', kwargs={'title_classe': title_classe})
        
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], 'examen supprimé !')
        
        results = Results.objects.filter(title='Contrôle Math', classe=self.classe)
        self.assertEqual(results.count(), 0)

    def test_delete_results_classe_not_found(self):
        self.client.force_login(self.teacher_user)
        
        title_classe = 'Contrôle Math-ClasseInexistante'
        delete_url = reverse('grades:delete_results', kwargs={'title_classe': title_classe})
        
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "L'examen n'a pas été supprimé !")


class GetCreatedTestCase(TestCase): 
    def setUp(self):
        self.client = Client()
        self.get_created_url = reverse('grades:get_created')
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)

    def test_get_created_success(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(self.get_created_url)        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})


class GetStudentResultsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_student_results_url = reverse('grades:get_student_results') 
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        self.classe = Classes.objects.create(name='6A')
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)

    def test_get_student_results_success(self):
        self.client.force_login(self.student_user)
        response = self.client.get(self.get_student_results_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})


class GetLastResultsTestCase(TestCase): 
    def setUp(self):
        self.client = Client()
        self.get_last_results_url = reverse('grades:get_last_results')
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        self.classe = Classes.objects.create(name='6A')
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)

    def test_get_last_results_success(self):
        self.client.force_login(self.student_user)
    
        response = self.client.get(self.get_last_results_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class ResultsModelTestCase(TestCase):
    def setUp(self):
        self.subject = Subjects.objects.create(name='Mathématiques')
        
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpassword123',
            first_name='John',
            last_name='Teacher',
            is_teacher=True
        )
        self.classe = Classes.objects.create(name='6A')
        self.teacher = Teachers.objects.create(user=self.teacher_user, subject=self.subject)
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='testpassword123',
            first_name='Jane',
            last_name='Student',
            is_student=True
        )
        self.student = Students.objects.create(user=self.student_user, classe=self.classe)

    def test_create_result_success(self):
        result = Results.objects.create(
            title='Contrôle Math',
            score=15.5,
            score_on=20,
            classe=self.classe,
            student=self.student,
            teacher=self.teacher
        )
        
        self.assertEqual(result.title, 'Contrôle Math')
        self.assertEqual(result.score, 15.5)
        self.assertEqual(result.score_on, 20)
        self.assertEqual(result.classe, self.classe)
        self.assertEqual(result.student, self.student)
        self.assertEqual(result.teacher, self.teacher)
        self.assertIsNotNone(result.added_date)

    def test_result_cascade_delete_classe(self):
        result = Results.objects.create(
            title='Contrôle Math',
            score=15.5,
            score_on=20,
            classe=self.classe,
            student=self.student,
            teacher=self.teacher
        )
        
        self.classe.delete()
        with self.assertRaises(Results.DoesNotExist):
            Results.objects.get(id=result.id)

    def test_result_set_null_teacher(self):  
        result = Results.objects.create(
            title='Contrôle Math',
            score=15.5,
            score_on=20,
            classe=self.classe,
            student=self.student,
            teacher=self.teacher
        )
        self.teacher.delete()
        updated_result = Results.objects.get(id=result.id)
        self.assertIsNone(updated_result.teacher)