from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from custom_auth.models import User
from school.models import Students, Teachers, Classes, Subjects
from .form import ExcelUploadForm
import pandas as pd
import secrets
import random 
from django.core.mail import send_mail
import environ
from django.urls import reverse

#load env variables
env = environ.Env()


@staff_member_required #only for admin
def admin_action_view(request):

    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)

        if form.is_valid():

            excel_file = request.FILES['fichier'] #get file
            df = pd.read_excel(excel_file) #make it a pandas dataframe

            for index, row in df.iterrows(): #iter over each row
                
                #check if value exist
                if row["is_student"] == "" or row["is_teacher"] == "" or row["first_name"] == "" or row['last_name'] == "":
                    continue

                 #create credentials
                new_email =f"{row["first_name"]}_{row['last_name'][:3]}{random.randint(0, 100)}@eme.com"
                new_email = new_email.lower() 
                new_password = secrets.token_urlsafe(7)

                #email info
                subject = 'MySchoolDesk | EME - Vos identifiants de connexion !'
                email_from = env('EMAIL_HOST_USER')

                #if student
                if row["is_student"] == True and row["classes"] != "":

                    #create user
                    user1 = User.objects.create_user(
                        email= new_email,
                        password= new_password, #generate random password
                        first_name=row["first_name"],
                        last_name=row["last_name"],
                        is_student = True,
                    )

                    #create or add to class 
                    try: # try if classe exist
                        classe1 = Classes.objects.get(name=row['classes'].lower()) #get classe
                        student1 = Students(id_user = user1, id_class = classe1) #create student
                        student1.save() #save to db
                    
                    except: # if classe not exist
                        classe1 = Classes(name = row['classes'].lower()) #create classe
                        classe1.save() #save to db
                        student1 = Students(id_user = user1, id_class = classe1) #create student
                        student1.save() #save to db

                    #sending email
                    message = f"""Bonjour {row['first_name']} {row['last_name']},

                                Bienvenue sur notre plateforme !

                                Voici vos identifiants de connexion personnels :

                                    Adresse e-mail : {new_email}
                                    Mot de passe : {new_password}

                                👉 Pour vous connecter, rendez-vous sur : https://localhost:8080/"""

                    send_mail( subject, message, email_from, [row['email']] )

                if row['is_teacher'] == True and row["subject"] != "":

                    #create user
                    user1 = User.objects.create_user(
                        email= new_email,
                        password= new_password, #generate random password
                        first_name=row["first_name"],
                        last_name=row["last_name"],
                        is_teacher = True,
                    )

                    #create teacher and assign subject created or existing subject 
                    try: # try if subject exist
                        subject1 = Subjects.objects.get(name=row['subject'].lower()) #get subject
                        teacher1 = Teachers(id_user = user1, id_subject = subject1) #create teacher
                        teacher1.save() #save to db
                    
                    except: # if subject not exist
                        subject1 = Subjects(name = row['subject'].lower()) #create subject
                        subject1.save() #save to db
                        teacher1 = Teachers(id_user = user1,id_subject = subject1) #create teacher
                        teacher1.save() #save to db

                    #sending email
                    message = f"""Bonjour {row['first_name']} {row['last_name']},

                                Bienvenue sur notre plateforme !

                                Voici vos identifiants de connexion personnels :

                                    Adresse e-mail : {new_email}
                                    Mot de passe : {new_password}

                                👉 Pour vous connecter, rendez-vous sur : https://localhost:8080/"""

                    send_mail( subject, message, email_from, [row['email']] )

            messages.success(request, "Importation réussie !")
            return redirect(reverse('admin:school_students_changelist'))
    else:
        form = ExcelUploadForm()        

    return render(request, "admin/msd_admin_action.html", {"form": form})
