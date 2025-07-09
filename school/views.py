from django.shortcuts import render

from rest_framework.decorators import api_view
from .models import Classes
from rest_framework.response import Response
from .serializers import ClassesSerializer

@api_view(['GET']) #get all classes names
def get_all_classes(request):
    all_classes = Classes.objects.all()
    return Response(ClassesSerializer(all_classes, many=True).data)