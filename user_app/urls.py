from django.urls import path
from .views import (
    UserView,
    LogoutView,
    SignUpView,
    LoginView,
    UserListView,
)

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

urlpatterns = [
    path('auth/users/<int:pk>/', UserView.as_view(), name='user-detail'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('users/', UserListView.as_view(), name='user-list'),
]