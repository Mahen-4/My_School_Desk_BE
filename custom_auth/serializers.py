from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    #optionnal field
    classe = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'is_teacher', 'is_student', 'classe', 'subject']
