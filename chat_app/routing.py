from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/support/', ChatConsumer.as_asgi()),
]