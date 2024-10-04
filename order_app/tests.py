from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from user_app.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Order
from product_app.models import Product,Category

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.category_1=Category.objects.create(name='1',slugname='yek')
        self.product_1 = Product.objects.create(name='yaser', slugname='yaseeer', category=self.category_1,stock=50, price=10000,description='ashkjgdbakjshdb')
        # Creating 3 orders
        self.order_1 = Order.objects.create(user=self.user, delivery_status='pending', delivery_date='2024-10-10', total_price=10000)
        self.order_2 = Order.objects.create(user=self.user, delivery_status='delivered', delivery_date='2024-10-01', total_price=10000)
        self.order_3 = Order.objects.create(user=self.user, delivery_status='delivered', delivery_date='2024-10-01', total_price=10000)

# tests.py

    def test_create_order(self):
        """Test creating a new order"""
        url = reverse('order-create')  
        data = {
            'user': self.user.id,
            'delivery_status': 'pending',
            'delivery_date': '2024-11-01',
            'total_price': 10000,
            'delivery_address': '123 Main St',
        "products": [
        self.product_1.id
    ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 4) 

    def test_retrieve_order(self):
        """Test retrieving a specific order"""
        url = reverse('order-detail', kwargs={'pk': self.order_1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['delivery_status'], self.order_1.delivery_status)

    def test_update_order(self):
        """Test updating an order"""
        url = reverse('order-detail', kwargs={'pk': self.order_1.id})
        data = {'delivery_status': 'shipped'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order_1.refresh_from_db()
        self.assertEqual(self.order_1.delivery_status, 'shipped')

    def test_delete_order(self):
        """Test deleting an order"""
        url = reverse('order-detail', kwargs={'pk': self.order_1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 2)  # Only two orders should remain after deletion

    def test_list_orders(self):
        """Test listing orders with filtering and sorting"""
        url = reverse('order-list')
        response = self.client.get(url, {'deliveryStatus': 'pending', 'sort': 'asc'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should only return the 'pending' order

    def test_pagination(self):
        """Test pagination for order listing"""
        url = reverse('order-list')
        response = self.client.get(url, {'page': 1, 'page_size': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Since page_size=1, expect 1 result per page
