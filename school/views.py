from django.shortcuts import render

from rest_framework.decorators import api_view
from .models import Classes, Subjects
from rest_framework.response import Response
from .serializers import ClassesSerializer, SubjectsSerializer
from django.views.decorators.csrf import csrf_protect

@api_view(['GET']) #get all classes names
def get_all_classes(request):
    all_classes = Classes.objects.all()
    return Response(ClassesSerializer(all_classes, many=True).data)


@api_view(['GET']) #get all subjects names
def get_all_subjects(request):
    all_classes = Subjects.objects.all()
    return Response(SubjectsSerializer(all_classes, many=True).data)

@api_view(['POST'])
@csrf_protect
def get_classe_all_students(request):
    classe = Classes.objects.get(name=request.data)
    return Response(classe.get_classe_students())


