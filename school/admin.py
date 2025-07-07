from django.contrib import admin
from .models import Classes, Students, Subjects, Teachers 
# Register your models here.

admin.site.register(Classes)
admin.site.register(Students)
admin.site.register(Subjects)
admin.site.register(Teachers)
