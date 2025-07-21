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

  
class TestGetResultsCreated(TestCase):
    def setUp(self):
        
        # create teacher object
        self.teacher_user = User.objects.create_user(
            email="teacher@test.com",
            is_teacher=True
        )
        self.teacher = Teachers.objects.create(user=self.teacher_user)
        
        # create classe and student
        self.classe = Classes.objects.create(name="6ème A")
        
        self.student1 = Students.objects.create(
            user=User.objects.create_user(
                email="student1@test.com",
                first_name="Jean",
                last_name="Dupont"
            ),
            classe=self.classe
        )
        
        self.student2 = Students.objects.create(
            user=User.objects.create_user(
                email="student2@test.com", 
                first_name="Marie",
                last_name="Martin"
            ),
            classe=self.classe
        )

        
    def test_get_results_created_with_data(self):
        #with results
        # Création résultats
        Results.objects.create(
            title="Contrôle Maths",
            student=self.student1,
            teacher=self.teacher,
            classe=self.classe,
            score=15.0,
            score_on=20
        )
        
        Results.objects.create(
            title="Contrôle Maths", 
            student=self.student2,
            teacher=self.teacher,
            classe=self.classe,
            score=17.0,
            score_on=20
        )
        
        result = self.teacher.get_results_created()
        
        
        self.assertIn("Contrôle Maths-6ème A", result)
        self.assertEqual(len(result["Contrôle Maths-6ème A"]), 2)
        
        # check data
        student1_data = result["Contrôle Maths-6ème A"][0]
        self.assertEqual(student1_data["student_first_name"], "Jean")
        self.assertEqual(student1_data["student_last_name"], "Dupont") 
        self.assertEqual(student1_data["student_score"], 15.0)
        self.assertEqual(student1_data["result_on"], 20)