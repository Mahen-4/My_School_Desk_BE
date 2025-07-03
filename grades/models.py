from django.db import models
from django.core.validators import MinValueValidator
from school.models import Classes, Students, Teachers

# Create your models here.

class Results(models.Model):
    title = models.CharField(max_length=150, unique=True)
    score = models.FloatField(validators=[MinValueValidator(0)])
    added_date = models.DateField()
    score_on = models.IntegerField(validators=[MinValueValidator(0)])
    id_class = models.ForeignKey(Classes, on_delete=models.CASCADE ,related_name="class_results")
    id_student = models.ForeignKey(Students, on_delete=models.CASCADE ,related_name="student_results")
    id_teacher = models.ForeignKey(Teachers, on_delete=models.SET_NULL, null=True, blank=True, related_name="teacher_results")