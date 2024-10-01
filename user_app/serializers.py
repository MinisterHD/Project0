from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

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
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError('Must include "username" and "password"')

        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise serializers.ValidationError('Invalid credentials')

        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': user.username,
                'email': user.email,
            }
        }
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__' 


  

