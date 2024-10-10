import logging
from rest_framework import status, filters, permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import OrderSerializer, CartItemSerializer, CartSerializer
from product_app.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.views import APIView
logger = logging.getLogger(__name__)

# Orders

class CreateOrderAPIView(CreateAPIView):
    #permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        return order

    def create(self, request, *args, **kwargs):
        order_items_data = request.data.get('order_items', [])

        if not order_items_data:
            return Response({"detail": "No items in the order."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0  


        order = Order(user=request.user, delivery_address=request.data.get('delivery_address'))
        order_items = []  

        for item_data in order_items_data:
            try:
                product_id = item_data['product'] 
                quantity = item_data['quantity']  


                if product_id is None or quantity is None:
                    return Response({"detail": "Product ID and quantity must be provided."}, status=status.HTTP_400_BAD_REQUEST)

                product = Product.objects.get(id=product_id)
                if product.stock < quantity:
                    return Response({"detail": f"Not enough stock for {product.name}."}, status=status.HTTP_400_BAD_REQUEST)

                total_price += product.price * quantity

 
                order_item = OrderItem(order=order, product=product, quantity=quantity)
                order_items.append(order_item)

                product.stock -= quantity
                product.sales_count += quantity 
                product.save()

            except Product.DoesNotExist:
                return Response({"detail": f"Product with ID {product_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
            except KeyError as e:
                return Response({"detail": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


        order.total_price = total_price
        order.save()

        OrderItem.objects.bulk_create(order_items)

        return Response({"detail": "Order created successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)

class OrderAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    #permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    parser_classes = [JSONParser]

    def get_object(self):
        try:
            return super().get_object()
        except Order.DoesNotExist:
            raise NotFound(detail="Order not found", code=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except serializers.ValidationError as e:
            logger.error(f"Validation error: {e.detail}")
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Update failed: {str(e)}")
            return Response({"detail": f"Unable to update order: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return Response({"detail": "Unable to delete order"}, status=status.HTTP_400_BAD_REQUEST)
    def get_queryset(self):
        # Prefetch related order_items and their associated product to avoid extra queries
        return super().get_queryset().prefetch_related('order_items__product')
        
class OrderListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication] 
    #permission_classes = [permissions.IsAuthenticated]  
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['delivery_status', 'user', 'order_date'] 
    ordering_fields = ['delivery_date', 'order_date']
    ordering = ['-order_date']


    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        if 'deliveryStatus' in params:
            queryset = queryset.filter(delivery_status=params['deliveryStatus'])

        if self.request.query_params.get('sort') == 'asc':
            return queryset.order_by('delivery_date')
        
        if 'sort' in params:
            order_by = 'delivery_date' if params['sort'] == 'asc' else '-delivery_date' 
            queryset = queryset.order_by(order_by)

        return queryset

class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            if order.delivery_status != 'cancelled':
                order.cancel_order()
                return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Order is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Error cancelling order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Cart
class AddToCartAPIView(CreateAPIView):
    #permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if quantity <= 0:
            logger.warning(f"User {user.id} attempted to add a non-positive quantity for product {product_id}.")
            return Response({"detail": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.warning(f"User {user.id} tried to add a non-existent product with ID {product_id}.")
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        cart_serializer = CartSerializer(cart)
        logger.info(f"User {user.id} added product {product.id} to cart. Quantity: {cart_item.quantity}.")
        return Response({
            "detail": "Product added to cart.",
            "cart":cart_serializer.data
        }, status=status.HTTP_201_CREATED)

class CartItemAPIView(RetrieveUpdateDestroyAPIView):
    #permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_object(self, user, product_id):
        try:
            cart = Cart.objects.get(user=user)
            return CartItem.objects.get(cart=cart, product__id=product_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return None

    def get(self, request, product_id):
        cart_item = self.get_object(request.user, product_id)
        if cart_item:
            cart_serializer = CartSerializer(cart_item.cart) 
            return Response(cart_serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, product_id):
        cart_item = self.get_object(request.user, product_id)
        if cart_item:
            quantity = request.data.get('quantity')
            if quantity is None or quantity <= 0:
                return Response({"detail": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

            cart_item.quantity = quantity
            cart_item.save()

            cart_serializer = CartSerializer(cart_item.cart)  
            return Response({
                "detail": "Cart item updated.",
                "cart": cart_serializer.data  
            }, status=status.HTTP_200_OK)

        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, product_id):
        cart_item = self.get_object(request.user, product_id)
        if cart_item:
            cart = cart_item.cart
            cart_item.delete()

            cart_serializer = CartSerializer(cart)  
            return Response({
                "detail": "Product removed from cart.",
                "cart": cart_serializer.data 
            }, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
    
