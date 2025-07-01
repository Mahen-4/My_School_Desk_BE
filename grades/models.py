from django.db import models
from django.core.validators import MinValueValidator
from school.models import Classes, Students, Teachers

# Create your models here.

class Results(models.Model):
    result_title = models.CharField(max_length=150, unique=True)
    result_student = models.FloatField(validators=[MinValueValidator(0)])
    result_added_date = models.DateField()
    result_on = models.IntegerField(validators=[MinValueValidator(0)])
    id_class = models.ForeignKey(Classes, related_name="class_results")
    id_student = models.ForeignKey(Students, related_name="student_results")
    id_teacher = models.ForeignKey(Teachers, related_name="teacher_results")