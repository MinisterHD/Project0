
from .models import *
from .serializers import *
from .permissions import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics,filters
from rest_framework.generics import (CreateAPIView,RetrieveUpdateDestroyAPIView,
     ListAPIView,CreateAPIView)
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser 
from rest_framework_simplejwt.authentication import JWTAuthentication

#Category
class CreateCategoryAPIView(CreateAPIView):
    serializer_class = CategorySerializer 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 
    parser_classes = [JSONParser ]

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all() 
    serializer_class = CategorySerializer
    def get_queryset(self):
        queryset = super().get_queryset()  
        params = self.request.query_params
        if 'slugname' in params:
            queryset = queryset.filter(slugname=params['slugname'])
        return queryset    

class CategoryAPIView(RetrieveUpdateDestroyAPIView): 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [JSONParser ]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_url_kwarg = 'category_id'
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#SubCategory
class CreateSubcategoryAPIView(CreateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 
    parser_classes = [JSONParser ]

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
    
class SubcategoryAPIView(RetrieveUpdateDestroyAPIView): 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [JSONParser]
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    lookup_url_kwarg = 'subcategory_id'
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#Products
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
    
class CreateProductAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 
    parser_classes = [JSONParser ]

class ProductAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_url_kwarg = 'product_id'
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#Comments
class CommentListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Comment.objects.filter(product_id=product_id)
    
class CreateCommentAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = CommentSerializer
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CommentAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [JSONParser,MultiPartParser, FormParser ]

    lookup_url_kwarg = 'comment_id'
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(owner=self.request.user)
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#Rating
class CreateRatingAPIView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RatingAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    lookup_url_kwarg = 'rating_id'


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
