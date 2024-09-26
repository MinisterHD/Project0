from django.urls import path
from .views import (
    UserRetrieveUpdateAPIView,
    UserRetrieveUpdateDestroyAPIView,
    Logout,
    SignUp,
    LoginView,

)

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

urlpatterns = [
    path('users/<int:pk>/', UserRetrieveUpdateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-detail'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', Logout.as_view(), name='logout'),
    path('auth/signup/', SignUp.as_view(), name='signup'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]