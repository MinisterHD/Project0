from django.urls import path
from .views import (
    ProductListAPIView,
    CreateProductAPIView,
    CategoryListAPIView,
    SubcategoryListAPIView,
    CategoryAPIView,
    ProductAPIView,
    CreateCommentAPIView,
    CommentAPIView,
    CommentListAPIView,
    CreateCategoryAPIView,
    CreateSubcategoryAPIView,
    SubcategoryAPIView,
)

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

urlpatterns = [
   
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/create/', CreateProductAPIView.as_view(), name='product-create'),
    path('products/<int:pk>/', ProductAPIView.as_view(), name='product-management'),

    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/create/', CreateCategoryAPIView.as_view(), name='category-create'),
    path('category/<int:pk>/',CategoryAPIView.as_view(),name='category-management'),

    path('subcategory/', SubcategoryListAPIView.as_view(), name='subcategory-list'),
    path('subcategory/create/',CreateSubcategoryAPIView.as_view(),name='subcategory-create'),
    path('subcategory/<int:pk>/',SubcategoryAPIView.as_view(),name='subcategory-management'),

    path('products/<int:product_pk>/comments/', CommentListAPIView.as_view(), name='product-comments-list'),
    path('products/<int:product_pk>/comments/create/', CreateCommentAPIView.as_view(), name='product-comment-create'),
    path('products/<int:product_pk>/comments/<int:pk>/', CommentAPIView.as_view(), name='product-comment-detail'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]