from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
import json
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
import random 
import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
import environ
from custom_auth.models import User, Password_reset_token
from school.models import Students, Teachers, Classes, Subjects
from django.forms.models import model_to_dict
import uuid
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required

#load env variables
env = environ.Env()


#send csrftoken 
@ensure_csrf_cookie
def get_csrf(request):
    # set cookie csrf in navigateur
    return JsonResponse({"detail": "CSRF cookie set"})

@api_view(['POST'])    
@csrf_protect
def logIn(request):

    try:
        data = request.data #get data from front
        email = data.get("email")
        password = data.get("password")

        user = authenticate(request, email=email, password=password) #check if user exist and credentials correct

        # if yes send success and code a2f by mail
        if user is not None:

            request.session['user_email'] = user.email #put email to session

            #add to session digiCode et digiCode expire datetime
            random_digit_code = random.randint(100000, 999999) 
            request.session[f"digi_code{user.email}"] = make_password(str(random_digit_code)) #hash number 
            request.session[f"digi_code_expire{user.email}"] = str(datetime.datetime.now() +  datetime.timedelta(minutes=5)) # add 5 minute from now datetime
            
            #sending email
            subject = "MySchoolDesk - Votre code d'authentification à deux facteurs (2FA)"
            message = f"""Hi {user.first_name},
                    Votre code d'authentification à deux facteurs (2FA) est le suivant : {random_digit_code}
                    Ce code expirera dans 5 minutes. Si vous n'avez pas demandé ce code, veuillez sécuriser votre compte immédiatement.
                    Nous vous en remercions,
                    
                    MySchoolDesk | EME """

            email_from = env('EMAIL_HOST_USER')
            send_mail( subject, message, email_from, [user.email] )

            return JsonResponse({"success": "Authentification réussi"}, status=200)
        else:
            return JsonResponse({"error": "Utilisateur introuvable"}, status=404)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@api_view(['POST'])    
@csrf_protect
def digi_code_check(request):

    
   #check if code expired
    if request.session.get('user_email'):
        #get session data
        user_email = request.session.get('user_email')
        expire_time_str = request.session.get(f"digi_code_expire{user_email}")

        expire_time = datetime.datetime.strptime(expire_time_str, "%Y-%m-%d %H:%M:%S.%f") #convert to datetime
        
        #compare datetime 
        if datetime.datetime.now() > expire_time:    
            #if expired delete session new  data
            request.session.pop("user_email", None)
            request.session.pop(f"digi_code{user_email}", None)
            request.session.pop(f"digi_code_expire{user_email}", None)

            return JsonResponse({"error": "Code expiré"}, status=422)
        
        else: 
            #check if digi code match
            data = request.data #get data from front
            if check_password(data.get('digi_code'), request.session.get(f"digi_code{user_email}")):
                
                try:
                    user1 = User.objects.get(email=user_email) #find user
                    login(request, user1) #login

                    #delete session new  data
                    request.session.pop("user_email", None)
                    request.session.pop(f"digi_code{user_email}", None)
                    request.session.pop(f"digi_code_expire{user_email}", None)
                    
                    
                    serializer = UserSerializer(user1) #transform user1 to dict
                    data = serializer.data
                    #if user is student send also student id if user is teacher send teacher id 
                    if user1.is_student :  
                        data['classe'] = Students.objects.get(user=user1.id).classe.name

                    if user1.is_teacher : 
                        data['subject'] = Teachers.objects.get(user=user1.id).subject.name
                        
                    return Response(data, status=200)

                except:
                    return JsonResponse({'error': "Erreur de connexion"}, status=500)
                
            else:
                 return JsonResponse({'error': "Code incorrect"}, status=404)

    else:
        return JsonResponse({"error": "Non autorisé"}, status=401)
    
@api_view(['POST'])    
@csrf_protect
def reset_password(request):
    
    data = request.data #get data from front
    user_email = data.get('email')

    #if user email exist get user
    if User.objects.filter(email=user_email).exists() :
                
        user1 = User.objects.get(email=user_email)

        #if a token for this user already exist return error 
        if Password_reset_token.objects.filter(user=user1).exists():
            exist_and_valid_check = Password_reset_token(user=user1)
            if not exist_and_valid_check.is_expired():
                return JsonResponse({'error': 'Token déjà envoyé et toujours valide ! (attendre 10 minutes pour un nouveau email)'})
            else:
                exist_and_valid_check.delete() #if expired delete it 

        token = uuid.uuid4().hex # create uuid code

        token_to_db =  Password_reset_token(user=user1, token=make_password(str(token)))
        token_to_db.save() #add to table hash uuid token

        #sending email
        subject = 'MySchoolDesk - Lien de réinitialisation du mot de passe'
        message = f"""Hello {user1.first_name},
                Votre lien de réinitialisation du mot de passe est : http://localhost:8080/auth/change_mdp/{token}.
                Ce lien expirera dans 5 minutes. Si vous n'avez pas demandé ce code, veuillez sécuriser votre compte immédiatement.
                Nous vous en remercions,
                
                MySchoolDesk"""

        email_from = env('EMAIL_HOST_USER')
        send_mail( subject, message, email_from, [user_email] )

        return JsonResponse({"success": "Email envoyé"}, status=200)

    else:
        return JsonResponse({'error': "Email introuvable"}, status=404)

@api_view(['POST'])
@csrf_protect
def change_password(request):
    
    data = request.data #get data from front
    user_token = data.get('token')

    all_tokens = Password_reset_token.objects.all()

    # loop over all tokens and search correponding
    matched_token = None
    for one_token in all_tokens:
        if check_password(user_token, one_token.token):
            matched_token = one_token.token
            break

    if matched_token == None : return JsonResponse({'error': 'Token introuvable'}, status=400)

    try:
        token_obj = Password_reset_token.objects.get(token=matched_token)
        if token_obj.is_expired(): #if token expired delete it 
            token_obj.delete()
            return JsonResponse({'error': 'Token expiré'}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid token'}, status=400)


    # get user linked to token
    user1 = token_obj.user 
    new_password = data.get('password')
    if new_password:
        user1.set_password(new_password)  # hash password
        user1.save()
        token_obj.delete() #delete token from table
        return JsonResponse({'success': 'Mot de passe changé'}, status=200)
    else:
        return JsonResponse({'error': 'Mot de passe introuvable'}, status=400)

@api_view(['GET'])
@login_required
def user_data(request):
    user = request.user
    if user.is_student:  
        user.classe = Students.objects.get(user=user.id).classe.name

    if user.is_teacher :  
        user.subject = Teachers.objects.get(user=user.id).subject.name

    serializer = UserSerializer(user) #transform user to dict
    return Response(serializer.data)

@api_view(['POST'])
@csrf_protect
def logOut(request):
    try:
        logout(request)
        return JsonResponse({'success': "Déconnecté"}, status=200)
    except:
        return JsonResponse({'error': "Erreur de déconnexion"}, status=400)
