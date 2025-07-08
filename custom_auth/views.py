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
from custom_auth.models import User
from school.models import Students, Teachers
from django.forms.models import model_to_dict


#load env variables
env = environ.Env()


#send csrftoken 
@ensure_csrf_cookie
def get_csrf(request):
    # set cookie csrf in navigateur
    return JsonResponse({"detail": "CSRF cookie set"})

@csrf_protect
def logIn(request):
    #check if request POST
    if request.method != "POST":
        return JsonResponse({"error": f"Méthode erreur"}, status=405)

    try:
        data = json.loads(request.body) #get data from front
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
    

@csrf_protect
def digi_code_check(request):

    #check if request POST
    if request.method != "POST":
        return JsonResponse({"error": f"Méthode erreur"}, status=405)
    
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
            data = json.loads(request.body) #get data from front
            if check_password(data.get('digi_code'), request.session.get(f"digi_code{user_email}")):
                
                try:
                    user1 = User.objects.get(email=user_email) #find user

                    login(request, user1) #login

                    #delete session new  data
                    request.session.pop("user_email", None)
                    request.session.pop(f"digi_code{user_email}", None)
                    request.session.pop(f"digi_code_expire{user_email}", None)
                    

                    user_data = model_to_dict(user1)
                    user_data.pop('password', None) #delete password before sending to front
                    #if user is student send also student id if user is teacher send teacher id 
                    if user1.is_student == True :  user_data["id_student"] = Students.objects.get(id_user=user1.id).id                   
                    if user1.is_teacher == True :  user_data["id_teacher"] = Teachers.objects.get(id_user=user1.id).id

                    return JsonResponse(user_data, status=200)

                except:
                    return JsonResponse({'error': "Erreur de connexion"}, status=500)
                
            else:
                 return JsonResponse({'error': "Code incorrect"}, status=404)

    else:
        return JsonResponse({"error": "Non autorisé"}, status=401)