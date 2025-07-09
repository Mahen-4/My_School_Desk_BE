from django.shortcuts import render

from rest_framework.decorators import api_view
from school.models import Teachers, Classes
from .models import HomeWorks 
from rest_framework.response import Response
from django.http import JsonResponse
import datetime

@api_view(['GET'])
def get_all_homeworks_created_teacher(request):
    return Response(request.user.teacher.get_homeworks_created())


@api_view(['POST'])
def add_homework(request):
    data = request.data #get data from front
    due_date = datetime.datetime.strptime(data.get('due_date'), "%Y-%m-%d").date() #convert to date format
    
    try:            
        classe_assigned = Classes.objects.get(id=data.get('classe'))
        homework = HomeWorks(description=data.get('description'), due_date=due_date, classe=classe_assigned, teacher=request.user.teacher)
        homework.save()
        return JsonResponse({'success': "Devoir ajouté !"})
    except:
        return JsonResponse({"error": "Erreur lors de l'ajout !"})

