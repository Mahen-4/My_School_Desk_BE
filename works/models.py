from django.db import models
from school.models import Classes, Teachers

# Create your models here.
class HomeWorks(models.Model):
    description = models.TextField(max_length=250)
    created_at = models.DateField()
    due_date = models.DateField()
    id_class = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name="class_homeworks")
    id_teacher =  models.ForeignKey(Teachers, on_delete=models.CASCADE ,related_name="teacher_homeworks")