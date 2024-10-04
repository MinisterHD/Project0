from django.urls import path
from .views import (
    OrderAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
)




urlpatterns = [
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderAPIView.as_view(), name='order-detail'),

    

]



