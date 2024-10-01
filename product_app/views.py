
from django.db.models import Q
from .models import *
from .serializers import *
from .permissions import *

from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (CreateAPIView,RetrieveUpdateDestroyAPIView,
                                        ListAPIView,CreateAPIView)
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError,NotFound


#Category
class CreateCategoryAPIView(CreateAPIView):
  serializer_class = CategorySerializer
  permission_classes = [IsAuthenticated]
  authentication_classes = [JWTAuthentication]
  parser_classes = [JSONParser]

  def create(self, request, *args, **kwargs):
      serializer = self.get_serializer(data=request.data)
      try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
      except ValidationError as e:
          return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
          return Response({'error': 'An internal server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
    parser_classes = [JSONParser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_url_kwarg = 'category_id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound('Category not found.')

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'An error occurred while retrieving the category.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while updating the category.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'An error occurred while deleting the category.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#SubCategory
class CreateSubcategoryAPIView(CreateAPIView):
  queryset = Subcategory.objects.all()
  serializer_class = SubcategorySerializer
  permission_classes = [IsAuthenticated]
  authentication_classes = [JWTAuthentication]
  parser_classes = [JSONParser]

  def create(self, request, *args, **kwargs):
      serializer = self.get_serializer(data=request.data)
      try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
      except ValidationError as e:
          return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
          return Response({'error': 'An internal server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
       
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
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound('SubCategory not found.')

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'An error occurred while retrieving the SubCategory.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while updating the SubCategory.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'An error occurred while deleting the Subcategory.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#Products
class CreateProductAPIView(CreateAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
  permission_classes = [IsAuthenticated]  # Uncomment if needed
  authentication_classes = [JWTAuthentication]
  parser_classes = [JSONParser]

  def create(self, request, *args, **kwargs):
      serializer = self.get_serializer(data=request.data)
      try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(serializer.data, status=status.HTTP_201_CREATED)
      except ValidationError as e:
          return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
          return Response({'error': 'An internal server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter] 

    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        # Validate category and subcategory IDs using OR logic for flexibility
        category_id = params.get('category')
        subcategory_id = params.get('subcategory')
        if category_id or subcategory_id:
            try:
                if category_id:
                    Category.objects.get(id=category_id)
                if subcategory_id:
                    Subcategory.objects.get(id=subcategory_id)
            except (Category.DoesNotExist, Subcategory.DoesNotExist):
                raise ValidationError("Invalid category or subcategory ID(s) provided.")

        # Filter by category and subcategory using OR logic for flexibility
        if category_id or subcategory_id:
            queryset = queryset.filter(Q(category_id=category_id) | Q(subcategory_id=subcategory_id))

        # Filter by price range
        min_price = params.get('minPrice')
        max_price = params.get('maxPrice')
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price)) 


        # Sort by specified field, providing a default sort field if not provided
        sort_field = params.get('sort', 'category')
        if sort_field:
            queryset = queryset.order_by(sort_field)

        # Sort by price based on the 'sort_order' parameter
        sort_order = params.get('sort_order', 'asc')  # Default to ascending order
        if sort_order == 'desc':
            queryset = queryset.order_by('-price')  # Descending order
        else:
            queryset = queryset.order_by('price')  # Ascending order

        return queryset

class ProductAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_url_kwarg = 'product_id'
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound('Product not found.')

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'An error occurred while retrieving the Product.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while updating the Product.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'An error occurred while deleting the Product.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#Comments
class CreateCommentAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = CommentSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CommentListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Comment.objects.filter(product_id=product_id)
    
class CommentAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [JSONParser]

    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred while retrieving the comment.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while updating the comment.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Http404:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred while deleting the comment.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #PUT meothod updates
    #GET method retrieves
    #DELETE method deletes

#Rating
class CreateRatingAPIView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingCreateSerializer
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

class RatingListAPIView(ListAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'user']  

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params


        product_id = params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)


        user_id = params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset
    
class RatingAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = Rating.objects.all()
    serializer_class = RatingUpdateSerializer
    lookup_url_kwarg = 'rating_id'

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response({'error': 'Rating not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred while retrieving the rating.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError as e:
            return Response({'error': 'You do not have permission to update this rating.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': 'An error occurred while updating the rating.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Http404:
            return Response({'error': 'Rating not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred while deleting the rating.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)