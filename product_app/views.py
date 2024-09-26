from django.shortcuts import render
from .models import *
from order_app.models import Order
from .serializers import *
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

from rest_framework import permissions
from rest_framework.generics import CreateAPIView

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

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all() 

    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()  
        params = self.request.query_params
        if 'slugname' in params:
            queryset = queryset.filter(slugname=params['slugname'])

        return queryset    

class SubcategoryListAPIView(generics.ListAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

    
        if 'category' in params:
            category_id = params['category']
            queryset = queryset.filter(category_id=category_id)

        return queryset


class RetrieveProductAPIView(RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = ProductSerializer

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

   
        if 'category' in params:
            category_id = params['category']
            queryset = queryset.filter(category_id=category_id)


        if 'subcategory' in params:
            subcategory_id = params['subcategory']
            queryset = queryset.filter(subcategory_id=subcategory_id)

       
        if 'price' in params:
            min_price = params.get('price', {}).get('minPrice')
            max_price = params.get('price', {}).get('maxPrice')
            if min_price:
                queryset = queryset.filter(price__gte=min_price)
            if max_price:
                queryset = queryset.filter(price__lt=max_price)

    
        if 'sort' in params:
            order_by = params['sort']
            queryset = queryset.order_by(order_by)

        return queryset

class UpdateProductAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly] 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class CreateProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    pass

class DeleteProductAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer