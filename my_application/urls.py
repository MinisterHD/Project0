from django.urls import path
from .views import (
    UserRetrieveUpdateAPIView,
    UserRetrieveUpdateDestroyAPIView,
    Logout,
    SignUp,
    ProductListAPIView,
    CreateProductAPIView,
    RetrieveOrderAPIView,
    UpdateOrderAPIView,
    DeleteProductAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
    CategoryListAPIView,
    SubcategoryListAPIView,
    UpdateProductAPIView,
    LoginView,
    RetrieveProductAPIView,
)

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

urlpatterns = [
    path('users/<int:pk>/', UserRetrieveUpdateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-detail'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', Logout.as_view(), name='logout'),
    path('auth/signup/', SignUp.as_view(), name='signup'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/create/', CreateProductAPIView.as_view(), name='product-create'),
    path('products/<int:pk>/', RetrieveProductAPIView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', UpdateProductAPIView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', DeleteProductAPIView.as_view(), name='product-delete'),
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', RetrieveOrderAPIView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update/', UpdateOrderAPIView.as_view(), name='order-update'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('subcategories/', SubcategoryListAPIView.as_view(), name='subcategory-list'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]