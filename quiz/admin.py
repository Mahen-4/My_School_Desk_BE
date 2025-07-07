from django.contrib import admin
from .models import Quiz, Attempts, Assigned_quiz, Questions, Responses

# Register your models here.
admin.site.register(Quiz)
admin.site.register(Attempts)
admin.site.register(Assigned_quiz)
admin.site.register(Questions)
admin.site.register(Responses)