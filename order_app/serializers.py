from rest_framework import serializers
from .models import Order,CartItem,Cart,OrderItem
from product_app.serializers import ProductSerializer
from product_app.models import Product
from django.db import transaction



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Allow product IDs to be set

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)  # Change 'products' to 'order_items'
    total_price = serializers.IntegerField(read_only=True)  # Total price calculation

    class Meta:
        model = Order
        fields = ['user', 'delivery_address', 'delivery_status', 'total_price', 'order_date', 'delivery_date', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')  # Extract order items
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total_price = 0  # Initialize total price
            for item_data in order_items_data:
                # Create OrderItem instances
                order_item = OrderItem.objects.create(order=order, **item_data)
                total_price += order_item.product.price * order_item.quantity  # Calculate total price

            order.total_price = total_price  # Update total price in Order
            order.save()  # Save order with total price

        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_items', None)  # Extract order items

        instance.user = validated_data.get('user', instance.user)
        instance.delivery_address = validated_data.get('delivery_address', instance.delivery_address)
        instance.delivery_status = validated_data.get('delivery_status', instance.delivery_status)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.delivery_date = validated_data.get('delivery_date', instance.delivery_date)
        instance.save()

        if order_items_data:
            instance.order_items.all().delete()  # Clear existing order items
            total_price = 0  # Reset total price
            for item_data in order_items_data:
                order_item = OrderItem.objects.create(order=instance, **item_data)  # Create new order items
                total_price += order_item.product.price * order_item.quantity  # Calculate total price
            
            instance.total_price = total_price  # Update total price
            instance.save()  # Save updated order

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
