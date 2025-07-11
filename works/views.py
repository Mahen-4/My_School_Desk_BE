from django.shortcuts import render

from rest_framework.decorators import api_view
from school.models import Teachers, Classes
from .models import HomeWorks 
from rest_framework.response import Response
from django.http import JsonResponse
import datetime
from django.views.decorators.csrf import csrf_protect

@api_view(['GET'])
def get_all_homeworks_created_teacher(request):
    return Response(request.user.teacher.get_homeworks_created())

@api_view(['GET'])
def get_all_homeworks(request):
    return Response(request.user.student.classe.get_classe_homeworks())

@api_view(['POST'])
@csrf_protect
def add_homework(request):
    data = request.data #get data from front
    due_date = datetime.datetime.strptime(data.get('due_date'), "%Y-%m-%d").date() #convert to date format
    
    try:            
        classe_assigned = Classes.objects.get(name=data.get('classe'))
        homework = HomeWorks(description=data.get('description'), due_date=due_date, classe=classe_assigned, teacher=request.user.teacher)
        homework.save() #save homework to table
        return JsonResponse({'success': "Devoir ajouté !"})
    except:
        return JsonResponse({"error": "Erreur lors de l'ajout !"})

@api_view(['PUT'])
@csrf_protect
def edit_homework(request):
    data = request.data #get data from front
    due_date = datetime.datetime.strptime(data.get('due_date'), "%Y-%m-%d").date() #convert to date format

    try:
        #set new data
        homework = HomeWorks.objects.get(id=data.get('homework_id'))
        homework.description = data.get('description')
        homework.due_date = data.get('due_date')
        homework.classe = Classes.objects.get(name=data.get('classe'))
        homework.save()
        return JsonResponse({'success': "devoir modifié !"}, status=200)    
    except:
        return JsonResponse({'error': "erreur de modification !"}, status=400)    

@api_view(['DELETE'])
@csrf_protect
def delete_homework(request, id):
    
    try:
        homework = HomeWorks.objects.get(id=id)
        homework.delete()
        return JsonResponse({"success": "Devoirs supprimé !"}, status=200)
    
    except:
        return JsonResponse({'error': "Le devoirs n'a pas été supprimé !"}, status=400)    
