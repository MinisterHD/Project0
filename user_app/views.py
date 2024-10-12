from .models import *
from .serializers import *
from django.contrib.auth.hashers import make_password
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import CreateAPIView,GenericAPIView
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

#Auth
class SignUpView(CreateAPIView):
    serializer_class = UserSignUpSerializer
    parser_classes = [JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data['username']


            if User.objects.filter(username=username).exists():
                raise ValidationError({'username': _('Username already exists.')})


            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            user = serializer.save()

   
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

   
            response_data = {
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': access,
                }
            }

            return Response(data=response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(GenericAPIView):
    serializer_class = CustomTokenObtainPairSerializer
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logging.error(f'Error during login: {str(e)}')
            return Response({'errors': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            return Response(data={'message': f'Bye {request.user.username}!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(data={'message': 'An error occurred during logout.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#UserManagement
class UserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self):
        obj = super().get_object()
        
        if self.request.user.is_staff or obj.id == self.request.user.id:
            return obj
        
        raise PermissionDenied("You do not have permission to access this user's profile.")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'password' in request.data:
            request.data['password'] = make_password(request.data['password'])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['is_staff'] 

    def get_queryset(self):
        queryset = super().get_queryset()
        is_staff = self.request.query_params.get('is_staff', None)
        if is_staff is not None:
            is_staff = is_staff.lower()
            if is_staff == 'true':
                queryset = queryset.filter(is_staff=True)
            elif is_staff == 'false':
                queryset = queryset.filter(is_staff=False)
        return queryset