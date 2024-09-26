from rest_framework import serializers
from .models import *


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



#class CommentSerializer(serializers.ModelSerializer):
    #class Meta:
        #model = Comment
        #fields   = ('id', 'user', 'text', 'created_at')
        #read_only_fields = ('id', 'created_at')
