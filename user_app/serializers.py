from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed,ValidationError


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__' 

class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        # Custom validation logic here
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username already exists.'})  

        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            refresh = RefreshToken(data['refresh'])
            data['refresh'] = str(refresh)
            return data
        except AuthenticationFailed as exc:
            raise ValidationError({'detail': str(exc)}, code='authentication_failed')

  
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__' 
        read_only_fields=['user_permissions','groups']


  

