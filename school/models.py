from django.db import models
from auth.models import User
from django.core.validators import MinValueValidator
from collections import defaultdict

# Create your models here.

class Classes(models.Model):
    class_name = models.CharField(max_length=50)
        
    def get_class_homeworks(self): # function for students

        all_homeworks = {} #create dict

        #for each homework of the class create a dict by id containing details of each homework
        for homework in self.class_homeworks.all():
            all_homeworks[homework.id] = {
                "subject": homework.id_teacher.id_subject.subject_name,
                "description" : homework.homework_description,
                "due_date" : homework.homework_due_date
            }

        return all_homeworks


    def get_class_last_homeworks(self): # function for students

        last_homeworks = {} #create dict

        last5_homeworks = [homework for homework in self.class_homeworks.all()][-5:] # get last 5 homeworks

        #for each last 5 homework of the class create a dict by subject containing details of each homework
        for homework in last5_homeworks:
            last_homeworks[homework.id_teacher.id_subject.subject_name] = {
                "description" : homework.homework_description,
                "due_date" : homework.homework_due_date
            }

        return last_homeworks


class Students(models.Model):
    student_average = models.FloatField(min=0, null=True, blank=True, default=None, validators=[MinValueValidator(0)])
    id_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile" )
    id_class = models.ForeignKey(Classes, related_name="class_students")

    def calc_average(self): # get average of the students
        list_results = [result for result in self.student_results.all() ] #get all results as a list
        self.student_average = sum(list_results) / len(list_results) # get average
        self.save
        return self.student_average #return average

    def get_results_by_subject(self):

        result_by_subject = defaultdict(list) #create dict

        #for each result of the student create a dict by subject containing details of each exam
        for result in self.student_results.all():
            result_by_subject[result.id_teacher.id_subject.subject_name].append({
                "title": result.result_title,
                "result" : result.result_student,
                "result_on" : result.result_on,
                "result_added_date": result.result_added_date
            })

        return result_by_subject

    def get_last_results(self):
        last_results = {} #create dict

        last5_result = [result for result in self.student_results.all()][-5:] # get last 5 result

        #for each result of the 5 latest create a dict containing details of each exam
        for result in last5_result:
            last_results[result.result_title] = {
                "subject": result.id_teacher.id_subject.subject_name,
                "result" : result.result_student,
                "result_on" : result.result_on,
                "result_added_date": result.result_added_date
            }

        return last_results


class Subjects(models.Model):
    subject_name = models.CharField(max_length=100)


class Teachers(models.Model):
    id_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile" )
    id_subject = models.ForeignKey(Subjects)

    def get_homeworks_created(self):

        all_homeworks = {} #create dict

        #for each homework create a dict containing details of each homework
        for homework in self.teacher_homeworks.all():
            all_homeworks[homework.id] = {   
                "homework_description" : homework.homework_description,
                "homework_created_at" : homework.homework_created_at,
                "homework_due_date" : homework.homework_due_date,
                "class_name": homework.id_class.class_name
            }

        return all_homeworks

    def get_last_homeworks_created(self):
        last_homeworks = {} #create dict

        last5_homeworks = [homework for homework in self.teacher_homeworks.all()][-5:] # get last 5 result

        #for each result of the 5 latest create a dict containing details of each homework
        for homework in last5_homeworks:
            last_homeworks[homework.id] = {   
                "homework_description" : homework.homework_description,
                "homework_created_at" : homework.homework_created_at,
                "homework_due_date" : homework.homework_due_date,
                "class_name": homework.id_class.class_name
            }

        return last_homeworks


    def get_results_created(self):

        results_created = defaultdict(list) #create dict

        #for each result of the teacher create a dict containing details of each student rate by exam title and classe
        for result in self.teacher_results.all():
            results_created[result.result_title][result.id_class.class_name].append({
                "student_first_name" : result.id_student.id_user.first_name,
                "student_last_name" : result.id_student.id_user.first_name,
                "student_result" : result.result_student,
                "result_on" : result.result_on,
                "result_id" : result.id
            })

        return results_created