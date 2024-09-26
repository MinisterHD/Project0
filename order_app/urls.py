from django.urls import path
from .views import (
    RetrieveOrderAPIView,
    UpdateOrderAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
)

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)



urlpatterns = [
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', RetrieveOrderAPIView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update/', UpdateOrderAPIView.as_view(), name='order-update'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]



