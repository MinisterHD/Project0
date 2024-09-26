from rest_framework import serializers
from .models import *

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__' 

class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__' 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__' 


  

