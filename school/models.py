from django.db import models
from custom_auth.models import User
from django.core.validators import MinValueValidator
from collections import defaultdict

# Create your models here.

class Classes(models.Model):
    name = models.CharField(max_length=50)
        
    def __str__(self): #description methode
        return self.name


    def get_class_homeworks(self): # function for students

        all_homeworks = {} #create dict

        #for each homework of the class create a dict by id containing details of each homework
        for homework in self.class_homeworks.all():
            all_homeworks[homework.id] = {
                "subject": homework.id_teacher.id_subject.name,
                "description" : homework.description,
                "due_date" : homework.due_date
            }

        return all_homeworks


    def get_class_last_homeworks(self): # function for students

        last_homeworks = {} #create dict

        last5_homeworks = [homework for homework in self.class_homeworks.all()][-5:] # get last 5 homeworks

        #for each last 5 homework of the class create a dict by subject containing details of each homework
        for homework in last5_homeworks:
            last_homeworks[homework.id_teacher.id_subject.name] = {
                "description" : homework.description,
                "due_date" : homework.due_date
            }

        return last_homeworks

    def get_class_quiz(self):

        all_quiz = {}

        #for each question get the question :responses dict and add to array 
        for assign_quiz in self.class_quiz.all():
            all_quiz[assign_quiz.id_quiz] = {
                "quiz_title" : assign_quiz.id_quiz.title,
                "quiz_subject": assign_quiz.id_quiz.id_teacher.id_subject.name
            }

        return all_quiz

class Students(models.Model):
    average = models.FloatField(null=True, blank=True, default=None, validators=[MinValueValidator(0)])
    id_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile" )
    id_class = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, blank=True, related_name="class_students")

    def __str__(self): #description methode
        return f'{self.id_user.last_name.upper()} {self.id_user.first_name} - {self.id_class.name}'

    def calc_average(self): # get average of the students
        list_results = [result for result in self.student_results.all() ] #get all results as a list
        self.average = sum(list_results) / len(list_results) # get average
        self.save
        return self.average #return average

    def get_results_by_subject(self):

        result_by_subject = defaultdict(list) #create dict

        #for each result of the student create a dict by subject containing details of each exam
        for result in self.student_results.all():
            result_by_subject[result.id_teacher.id_subject.name].append({
                "title": result.title,
                "score" : result.score,
                "result_on" : result.score_on,
                "result_added_date": result.added_date
            })

        return result_by_subject

    def get_last_results(self):
        last_results = {} #create dict

        last5_result = [result for result in self.student_results.all()][-5:] # get last 5 result

        #for each result of the 5 latest create a dict containing details of each exam
        for result in last5_result:
            last_results[result.title] = {
                "subject": result.id_teacher.id_subject.name,
                "score" : result.score,
                "result_on" : result.score_on,
                "result_added_date": result.added_date
            }

        return last_results


class Subjects(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self): #description methode
            return self.name


class Teachers(models.Model):
    id_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile" )
    id_subject = models.ForeignKey(Subjects, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self): #description methode
        return f'{self.id_user.last_name.upper()} {self.id_user.first_name} - {self.id_subject.name}'


    def get_homeworks_created(self):

        all_homeworks = {} #create dict

        #for each homework create a dict containing details of each homework
        for homework in self.teacher_homeworks.all():
            all_homeworks[homework.id] = {   
                "homework_description" : homework.description,
                "homework_created_at" : homework.created_at,
                "homework_due_date" : homework.due_date,
                "class_name": homework.id_class.name
            }

        return all_homeworks

    def get_last_homeworks_created(self):
        last_homeworks = {} #create dict

        last5_homeworks = [homework for homework in self.teacher_homeworks.all()][-5:] # get last 5 result

        #for each result of the 5 latest create a dict containing details of each homework
        for homework in last5_homeworks:
            last_homeworks[homework.id] = {   
                "homework_description" : homework.description,
                "homework_created_at" : homework.created_at,
                "homework_due_date" : homework.due_date,
                "class_name": homework.id_class.name
            }

        return last_homeworks


    def get_results_created(self):

        results_created = defaultdict(list) #create dict

        #for each result of the teacher create a dict containing details of each student rate by exam title and classe
        for result in self.teacher_results.all():
            results_created[result.title][result.id_class.name].append({
                "student_first_name" : result.id_student.id_user.first_name,
                "student_last_name" : result.id_student.id_user.last_name,
                "student_score" : result.score,
                "result_on" : result.score_on,
                "result_id" : result.id
            })

        return results_created
    

    def get_quiz_created(self):

        all_quiz_created = {}

        #get all quiz created by the teacher and return the dict with all (title + the id)
        for quiz in self.teacher_quiz.all():
            all_quiz_created[quiz.id] = {"quiz_title": quiz.title}

        return all_quiz_created    