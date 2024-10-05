from rest_framework import serializers
from .models import Order,CartItem,Cart
from product_app.serializers import ProductSerializer
from product_app.models import Product
from django.db import transaction



class OrderSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all(), write_only=True)
    product_details = ProductSerializer(many=True, read_only=True, source='products')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['user', 'delivery_address', 'delivery_status', 'total_price', 'order_date', 'delivery_date', 'products', 'product_details']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            order.products.set(products_data)
            total_price = sum(product.price for product in products_data)
            order.total_price = total_price
            order.save()

        return order


        
    def update(self, instance, validated_data):
        products_data = validated_data.pop('products', None)

        instance.user = validated_data.get('user', instance.user)
        instance.delivery_address = validated_data.get('delivery_address', instance.delivery_address)
        instance.delivery_status = validated_data.get('delivery_status', instance.delivery_status)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.delivery_date = validated_data.get('delivery_date', instance.delivery_date)
        instance.save()

        if products_data:
            instance.products.set(products_data)
            total_price = sum(product.price for product in Product.objects.filter(id__in=products_data))
            instance.total_price = total_price
            instance.save()

        return instance

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) 

    class Meta:
        model = CartItem
        exclude = ['cart'] 

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True)  

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items'] 
