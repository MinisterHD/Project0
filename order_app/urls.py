from django.urls import path
from .views import (
    OrderAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
    CartItemAPIView,
    AddToCartAPIView,
    CancelOrderAPIView,
    UserCartAPIView,
    UserOrdersAPIView,
)




urlpatterns = [
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderAPIView.as_view(), name='order-detail'),
    path('orders/cancel/<int:order_id>/', CancelOrderAPIView.as_view(), name='cancel-order'),
    path('orders/user/<int:user_id>/', UserOrdersAPIView.as_view(), name='user-orders'),

    path('cart/add/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('cart/<int:user_id>/item/<int:product_id>/', CartItemAPIView.as_view(), name='cart-item-detail'),
    path('cart/<int:user_id>/', UserCartAPIView.as_view(), name='user-cart'),
  ]



