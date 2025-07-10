from rest_framework import serializers
from .models import Classes, Subjects

class ClassesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classes
        fields = ['id', 'name']

class SubjectsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subjects
        fields = ['id', 'name']
