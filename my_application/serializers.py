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

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__' 



class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'  

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product 

        fields = '__all__' 
  

class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'  