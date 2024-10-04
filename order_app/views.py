import logging
from rest_framework import status, filters, permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Order
from .serializers import OrderSerializer

logger = logging.getLogger(__name__)

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

        # Filter by delivery status
        if 'deliveryStatus' in params:
            queryset = queryset.filter(delivery_status=params['deliveryStatus'])

        # Sorting based on delivery date (asc/desc)
        if 'sort' in params:
            order_by = 'delivery_date' if params['sort'] == 'asc' else '-deliveryDate'
            queryset = queryset.order_by(order_by)

        return queryset
