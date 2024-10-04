import logging
from rest_framework import status, filters, permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import OrderSerializer,CartItemSerializer
from product_app.models import Product
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

#Orders
class OrderPagination(PageNumberPagination):
    page_size = 1 
    page_size_query_param = 'page_size'
    max_page_size = 10

class CreateOrderAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated] 
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]  # JWT Authentication
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can retrieve, update, or delete
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    parser_classes = [JSONParser]  # Parse JSON data

    def get_object(self):
        try:
            return super().get_object()
        except Order.DoesNotExist:
            raise NotFound(detail="Order not found", code=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Update failed: {e}")  # Log the error
            return Response({"detail": "Unable to update order"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Delete failed: {e}")  # Log the error
            return Response({"detail": "Unable to delete order"}, status=status.HTTP_400_BAD_REQUEST)

class OrderListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [permissions.IsAuthenticated]  
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['delivery_status', 'user', 'order_date'] 
    pagination_class = OrderPagination  

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        if 'deliveryStatus' in params:
            queryset = queryset.filter(delivery_status=params['deliveryStatus'])

        if 'sort' in params:
            order_by = 'delivery_date' if params['sort'] == 'asc' else '-deliveryDate'
            queryset = queryset.order_by(order_by)

        return queryset

#Cart
class AddToCartAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

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

        logger.info(f"User {user.id} added product {product.id} to cart. Quantity: {cart_item.quantity}.")
        return Response({
            "detail": "Product added to cart.",
            "product_id": product.id,
            "quantity": cart_item.quantity
        }, status=status.HTTP_201_CREATED)

class CartItemAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_object(self, user, product_id):
        """Retrieve the CartItem object for the user and product ID."""
        try:
            cart = Cart.objects.get(user=user)
            return CartItem.objects.get(cart=cart, product__id=product_id)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return None

    def get(self, request, product_id):
        """Retrieve a specific cart item with detailed product info."""
        cart_item = self.get_object(request.user, product_id)
        if cart_item:
            serializer = CartItemSerializer(cart_item) 
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)


    def put(self, request, product_id):
        """Update the quantity of a specific cart item."""
        cart_item = self.get_object(request.user, product_id)
        if cart_item:
            quantity = request.data.get('quantity')
            if quantity is None or quantity <= 0:
                return Response({"detail": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

            cart_item.quantity = quantity
            cart_item.save()
            return Response({"detail": "Cart item updated."}, status=status.HTTP_200_OK)

        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, product_id):
        """Remove a specific cart item."""
        cart_item = self.get_object(request.user, product_id)
        if cart_item:
            cart_item.delete()
            return Response({"detail": "Product removed from cart."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)