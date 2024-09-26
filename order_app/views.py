from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,RetrieveAPIView,RetrieveUpdateAPIView
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_204_NO_CONTENT,HTTP_201_CREATED
from django.contrib.auth.hashers import make_password
from rest_framework import filters
from rest_framework.generics import ListAPIView
from .serializers import OrderSerializer
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from .serializers import OrderSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.generics import DestroyAPIView
from rest_framework.decorators import api_view

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.exceptions import ValidationError
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class CreateOrderAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class RetrieveOrderAPIView(RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class UpdateOrderAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]  
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderListAPIView(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

      
        if 'deliveryStatus' in params:
            queryset = queryset.filter(delivery_status=params['deliveryStatus'])

       
        if 'sort' in params:
            order_by = 'deliveryDate' if params['sort'] == 'asc' else '-deliveryDate'
            queryset = queryset.order_by(order_by)

        return queryset

