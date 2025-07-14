from django.shortcuts import render

from rest_framework.decorators import api_view
from school.models import Classes, Students
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Results
from django.views.decorators.csrf import csrf_protect

@api_view(['POST'])
@csrf_protect
def add_results(request):
    data = request.data #get data

    try:
        #get base data 
        title = data.get('title')
        result_on = data.get('result_on')
        classe  = Classes.objects.get(name=data.get('classe_name'))


        #loop over all results and add to db
        for key, score in data.get('all_results').items():
            try:
                result1 = Results(
                    title=title, 
                    score=score, 
                    score_on=result_on, 
                    classe=classe, 
                    student= Students.objects.get(id=key),
                    teacher= request.user.teacher
                    )
                result1.save()
            except:
                return JsonResponse({"error": f"Erreur d'ajout pour {key}"})

        return JsonResponse({"success": "Résultats ajoutés"}, status=200)   
    
    except:
        return JsonResponse({"error": "Erreur d'ajout"})

@api_view(['GET'])
def get_created(request):
    return Response(request.user.teacher.get_results_created())


@api_view(['PUT'])
@csrf_protect
def edit_result(request):
    data = request.data
    try:
        #loop over alll results to edit 
        for key, result in data.get('all_results').items():
            #edit field and save
            result1 = Results.objects.get(id=key)
            result1.title = data.get('title')
            result1.score_on = data.get('result_on')
            result1.score = result
            result1.save()

        return JsonResponse({"success": "Résultat(s) modifié(s)"}, status=200)
    except:
        return JsonResponse({"error": "Erreur de modification des résultats"}, status=400)
    

@api_view(['DELETE'])
@csrf_protect
def delete_results(request, title_classe):
    
    #split title_classe
    title = title_classe.split('-')[0]
    classe_name = title_classe.split('-')[1]
    try:
        #get all results with this title and this classe and delete
        classe = Classes.objects.get(name=classe_name)
        results = Results.objects.filter(title=title, classe=classe).all()
        for result in results:
            result.delete()

        return JsonResponse({"success": "examen supprimé !"}, status=200)
    
    except:
        return JsonResponse({'error': "L'examen n'a pas été supprimé !"}, status=400)    

@api_view(['GET'])
def get_student_results(request):
    return Response(request.user.student.get_results_by_subject())


@api_view(['GET'])
@csrf_protect
def get_last_results(request):
    return Response(request.user.student.get_last_results())