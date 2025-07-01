from django.db import models
from school.models import Classes, Teachers

# Create your models here.
class HomeWorks(models.Model):
    homework_description = models.TextField(max_length=250)
    homework_created_at = models.DateField()
    homework_due_date = models.DateField()
    id_class = models.ForeignKey(Classes,related_name="class_homeworks")
    id_teacher =  models.ForeignKey(Teachers, related_name="teacher_homeworks")