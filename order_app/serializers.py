from rest_framework import serializers
from .models import *
from product_app.serializers import ProductSerializer

class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'  
