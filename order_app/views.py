import logging
from rest_framework import status, filters, permissions, generics
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import OrderSerializer, CartItemSerializer, CartSerializer
from product_app.models import Product
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
from rest_framework import serializers
from rest_framework.views import APIView
from .permissions import IsOwnerOrAdmin,IsAdminOrReadOnly
from django.db import IntegrityError, transaction

logger = logging.getLogger(__name__)

class UserOrdersAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['delivery_status', 'order_date']
    ordering_fields = ['delivery_date', 'order_date']
    ordering = ['-order_date']

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Order.objects.filter(user_id=user_id).prefetch_related('order_items__product')

class OrderAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly,IsAdminOrReadOnly]
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
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        return super().get_queryset().prefetch_related('order_items__product')

class CreateOrderAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
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
        delivery_status = request.data.get('delivery_status', 'pending')

        order = Order(
            user=request.user, 
            delivery_address=request.data.get('delivery_address'),
            delivery_status=delivery_status  
        )
        order_items = []  

        try:
            with transaction.atomic():
                for item_data in order_items_data:
                    product_id = item_data.get('product') 
                    quantity = item_data.get('quantity')  

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

                order.total_price = total_price
                order.save()
                OrderItem.objects.bulk_create(order_items)

                return Response({"detail": "Order created successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"detail": f"Product with ID {product_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response({"detail": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAdminUser]  
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
    permission_classes = [IsOwnerOrAdmin]

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
            logger.error(f"Error cancelling order: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Cart
class AddToCartAPIView(CreateAPIView):
    permission_classes = [IsOwnerOrAdmin]

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

        try:
            with transaction.atomic():
                cart, created = Cart.objects.get_or_create(user=user)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                cart_item.quantity += quantity
                cart_item.save()
                cart_serializer = CartSerializer(cart)
                logger.info(f"User {user.id} added product {product.id} to cart. Quantity: {cart_item.quantity}.")
                return Response({
                    "detail": "Product added to cart.",
                    "cart": cart_serializer.data
                }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CartItemAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_object(self):
        user_id = self.kwargs['user_id']
        product_id = self.kwargs['product_id']
        try:
            user = User.objects.get(id=user_id)
            cart = Cart.objects.get(user=user)
            return CartItem.objects.get(cart=cart, product__id=product_id)
        except (User.DoesNotExist, Cart.DoesNotExist, CartItem.DoesNotExist):
            return None

    def get(self, request, user_id, product_id):
        try:
            cart_item = self.get_object()
            if cart_item:
                cart_serializer = CartSerializer(cart_item.cart)
                return Response(cart_serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving cart item: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, user_id, product_id):
        try:
            cart_item = self.get_object()
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
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, user_id, product_id):
        try:
            cart_item = self.get_object()
            if cart_item:
                cart = cart_item.cart
                cart_item.delete()
                cart_serializer = CartSerializer(cart)
                return Response({
                    "detail": "Product removed from cart.",
                    "cart": cart_serializer.data
                }, status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting cart item: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserCartAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_object(self):
        try:
            return Cart.objects.get(user=self.request.user)
        except Cart.DoesNotExist:
            return None

    def get(self, request):
        try:
            cart = self.get_object()
            if cart:
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving user cart: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)