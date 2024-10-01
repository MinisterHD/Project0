from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

class SignUpViewTests(APITestCase):
    def test_signup_success(self):
        url = reverse('signup')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'testuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_signup_username_exists(self):
        User.objects.create_user(username='testuser', password='testpassword')
        url = reverse('signup')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'testuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data['errors'])

class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_success(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)

class UserViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_update_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        data = {'username': 'updateduser'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_delete_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

class LogoutViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.token = RefreshToken.for_user(self.user)

    def test_logout_success(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('message', response.data)

class UserListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin', password='admin123', email='admin@example.com'
        )
        self.regular_user = User.objects.create_user(
            username='user', password='user123', email='user@example.com'
        )
        self.url = reverse('user-list')  # Make sure this matches your URL name

    def test_user_list_as_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())

    def test_user_list_as_non_admin(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

