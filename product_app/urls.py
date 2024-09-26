from django.urls import path
from .views import (
    
    ProductListAPIView,
    CreateProductAPIView,
    DeleteProductAPIView,
    UpdateProductAPIView,
    RetrieveProductAPIView,
    CategoryListAPIView,
    SubcategoryListAPIView
)

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

urlpatterns = [
   
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/create/', CreateProductAPIView.as_view(), name='product-create'),
    path('products/<int:pk>/', RetrieveProductAPIView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', UpdateProductAPIView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', DeleteProductAPIView.as_view(), name='product-delete'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('subcategories/', SubcategoryListAPIView.as_view(), name='subcategory-list'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]