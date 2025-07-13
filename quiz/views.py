from django.shortcuts import render
from rest_framework.decorators import api_view
from school.models import Classes, Subjects
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .models import Quiz, Questions, Responses, Attempts
from django.forms.models import model_to_dict


@api_view(['POST'])
@csrf_protect
def add_quiz(request):

    data = request.data

    try:
        #create object quiz
        quiz1 = Quiz.objects.create(title=data.get('title'), description=data.get('description'), teacher=request.user.teacher)


        classes_obj_list = [] #array of object
        #add classes assigned to array 
        for classe in data.get('classes'):
            try:
                classe_obj = Classes.objects.get(name=classe)
                classes_obj_list.append(classe_obj)
            except Classes.DoesNotExist:
                return JsonResponse({'error': "Classe invalide"}, status=400)

        #set classes 
        quiz1.classes.set(classes_obj_list)


        #loop over all question and their responses
        for key_question, value_responses in data.get('questions_responses').items():
            
            #create question in db
            question1 = Questions.objects.create(title=key_question, quiz=quiz1)
            #create responses in db
            for response in value_responses:
                response1 = Responses.objects.create(title=response['text'], is_answer=response['is_answer'], question=question1)
        
        return JsonResponse({'success': "quiz ajouté"}, status=200)
    
    except:
        return JsonResponse({"error": 'Erreur lors de la création du quiz'}, status=400)

@api_view(['GET'])
@csrf_protect
def get_teacher_created_quiz(request):
    return Response(request.user.teacher.get_quiz_created())


@api_view(['POST'])
@csrf_protect
def get_quiz_questions_responses(request):
    data = request.data
    try:
        quiz1 = Quiz.objects.get(id=data)
        return Response(quiz1.get_questions_responses())
    except:
        return JsonResponse({"error": "Quiz introuvable"})

@api_view(['PUT'])
@csrf_protect
def edit_quiz(request):

    data = request.data

    try:
        #get object quiz
        quiz1 = Quiz.objects.get(id=data.get('quiz_id'))
        quiz1.title = data.get('title')
        quiz1.description = data.get('description')
        quiz1.save()

        classes_obj_list = [] #array of object
        #add classes assigned to array 
        for classe in data.get('classes'):
            try:
                classe_obj = Classes.objects.get(name=classe)
                classes_obj_list.append(classe_obj)
            except Classes.DoesNotExist:
                return JsonResponse({'error': "Classe invalide"}, status=400)

        #set/update classes 
        quiz1.classes.set(classes_obj_list)


        #loop over all question and their responses
        for key_question, value_responses in data.get('questions_responses').items():
            
            #get question in db
            question1 = Questions.objects.get(id=value_responses[0]['question_id'])
            question1.title = key_question #change title
            question1.save()

            #get responses in db and edit
            for response in value_responses:
                response1 = Responses.objects.get(id=response['response_id'])
                response1.title = response['response_title']
                response1.is_answer = response['is_answer']
                response1.save()
        
        return JsonResponse({'success': "quiz ajouté"}, status=200)
    
    except:
        return JsonResponse({"error": 'Erreur lors de la modification du quiz'}, status=400)

@api_view(['DELETE'])
@csrf_protect
def delete_question(request, id):
    try:
        question1 = Questions.objects.get(id=id)
        question1.delete()
        return JsonResponse({"success": "Question supprimée !"}, status=200)
    
    except:
        return JsonResponse({'error': "La question n'a pas été supprimée !"}, status=400)    


@api_view(['DELETE'])
@csrf_protect
def delete_quiz(request, id):
    try:
        quiz1 = Quiz.objects.get(id=id)
        quiz1.delete()
        return JsonResponse({"success": "Quiz supprimé !"}, status=200)
    
    except:
        return JsonResponse({'error': "Le Quiz n'a pas été supprimé !"}, status=400)    


@api_view(['GET'])
def get_classe_quiz(request):
    return Response(request.user.student.classe.get_classe_quiz())

@api_view(['POST'])
@csrf_protect
def get_quiz_info(request):
    data = request.data
    try:
        quiz1 = Quiz.objects.get(id=data)
        try:
            attempt = Attempts.objects.get(quiz=quiz1, student=request.user.student)

            #returning data add attempt data to the dict returned by the function get_quiz_info
            return_data = quiz1.get_quiz_info()
            return_data['date_last_attempt']  = attempt.date_attempted.strftime('%d-%m-%Y')
            return_data['last_score'] = attempt.score

            return Response(return_data)
        
        except Exception as e:
            return Response(quiz1.get_quiz_info())
        
    except:
        return JsonResponse({"error": "Quiz introuvable "})
    

@api_view(['POST'])
@csrf_protect
def add_attempt(request):
    data = request.data   

    #check if already attempted
    attempt1 = Attempts.objects.filter(student=request.user.student,quiz=Quiz.objects.get(id=data.get('quiz_id'))) 

    if attempt1.exists():
        try:
            #save on existing attempt
            attempt1.score = data.get('score')
            attempt1.save()
            return JsonResponse({"success": "Mise à jour réussie"})
        except:
            return JsonResponse({"error": "Mise à jour de la tentative invalide"})

    else:
        try:
            #create new attempts
            attempt1 = Attempts(
                student=request.user.student,
                quiz=Quiz.objects.get(id=data.get('quiz_id')),
                score=data.get('score')
                )
            attempt1.save()
            return JsonResponse({"success": "Insertion réussie"})
        except:
            return JsonResponse({"error": "Insertion de la tentative invalide"})