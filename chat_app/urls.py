# chat/urls.py
from django.urls import path
from .views import ChatMessageViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'chat/messages', ChatMessageViewSet)

urlpatterns = router.urls  
