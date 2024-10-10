from django.urls import path
from .views import (
    OrderAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
    CartItemAPIView,
    AddToCartAPIView,
    CancelOrderAPIView
)




urlpatterns = [
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderAPIView.as_view(), name='order-detail'),

    path('cart/add/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('cart/<int:product_id>/', CartItemAPIView.as_view(), name='cart-item'),
    path('orders/cancel/<int:order_id>/', CancelOrderAPIView.as_view(), name='cancel-order'),
]



