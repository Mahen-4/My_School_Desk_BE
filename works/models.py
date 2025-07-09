from django.db import models
from school.models import Classes, Teachers

# Create your models here.
class HomeWorks(models.Model):
    description = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name="classe_homeworks", null=False)
    teacher =  models.ForeignKey(Teachers, on_delete=models.CASCADE ,related_name="teacher_homeworks")