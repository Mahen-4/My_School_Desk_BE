from django.db import models
from school.models import Teachers, Classes, Students
from django.core.validators import MinValueValidator
from collections import defaultdict

class Quiz(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=250, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teachers, on_delete=models.CASCADE, related_name="teacher_quiz")
    classes = models.ManyToManyField(Classes, through="Assigned_quiz")
    students = models.ManyToManyField(Students, through='Attempts')

    def get_questions_responses(self):

        questions_responses = {}

        #get question and responses
        for question in self.quiz_questions.all():
            questions_responses[question.title] = [
                {
                    'response_title': response.title,
                    'is_answer': response.is_answer,
                    'question_id': question.id,
                    'response_id': response.id,
                }
                for response in question.question_responses.all()
            ]

        return questions_responses

    def get_quiz_info(self):
        return {self.id : {
            "quiz_title": self.title,
            "quiz_description": self.description,
            "quiz_added_date": self.added_date.strftime('%d-%m-%Y'),
            "quiz_teacher" : f'{self.teacher.user.last_name.upper()} {self.teacher.user.first_name}',
            "quiz_teacher_subject" : self.teacher.subject.name
        }}

class Attempts(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.CharField(max_length=50)
    date_attempted = models.DateTimeField(auto_now_add=True)
    
class Assigned_quiz(models.Model):
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='classe_quiz') 
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

class Questions(models.Model):
    title = models.TextField(max_length=250)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_questions")

    def get_responses(self):
        all_responses = defaultdict(list) #init dict
        
        #for each responses of the question create an unique dict containing data about the responses
        for response in self.question_responses.all():
            all_responses[self.title].append({
                'response_title': response.title,
                'is_answer': response.is_answer,
                'question_id': self.id,
                'response_id': response.id,
            })

        return all_responses

class Responses(models.Model):
    title = models.TextField(max_length=250)
    is_answer = models.BooleanField()
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="question_responses")




