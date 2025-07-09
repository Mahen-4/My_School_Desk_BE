from django.urls import path, include
from . import views

urlpatterns = [
    path('classes/all', views.get_all_classes),
]