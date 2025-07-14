from django.urls import path, include
from . import views

urlpatterns = [
    path('csrf/', views.get_csrf, name="csrf"),
    path('login/', views.logIn,  name="login"),
    path('digi_code_check/',views.digi_code_check, name="digi_code_check"),
    path('reset_password/', views.reset_password,  name="reset_password"),
    path('change_password/', views.change_password, name="change_password"),
    path('user_data/', views.user_data, name="user_data"),
    path('logout/', views.logOut, name="logout")
]