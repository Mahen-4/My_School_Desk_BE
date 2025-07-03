from django.db import models
from school.models import Teachers, Classes, Students
from django.core.validators import MinValueValidator
from collections import defaultdict

class Quiz(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=250)
    added_date = models.DateField()
    id_teacher = models.ForeignKey(Teachers, on_delete=models.CASCADE, related_name="teacher_quiz")
    classes = models.ManyToManyField(Classes, through="Assigned_quiz")
    students = models.ManyToManyField(Students, through='Attempts')

    def get_questions_responses(self):

        all_questions_responses = []

        #for each question get the question :responses dict and add to array 
        for question in self.quiz_questions.all():
            all_questions_responses.append(question.get_responses())

        return all_questions_responses

class Attempts(models.Model):
    id_student = models.ForeignKey(Students, on_delete=models.CASCADE)
    id_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(validators=[MinValueValidator(0)])
    date_attempted = models.DateField()
    
class Assigned_quiz(models.Model):
    id_class = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='class_quiz') 
    id_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

class Questions(models.Model):
    title = models.TextField(max_length=250)
    id_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_questions")

    def get_responses(self):
        all_responses = defaultdict(list) #init dict
        
        #for each responses of the question create an unique dict containing data about the responses
        for response in self.question_responses.all():
            all_responses[self.title].append({
                'response_title': response.title,
                'is_answer': response.is_answer
            })

        return all_responses

class Responses(models.Model):
    title = models.TextField(max_length=250)
    is_answer = models.BooleanField()
    id_question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="question_responses")




