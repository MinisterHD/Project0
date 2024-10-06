from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from user_app.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Order, Cart, CartItem, OrderItem  # Import OrderItem
from product_app.models import Product, Category

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.category_1 = Category.objects.create(name='1', slugname='yek')
        self.product_1 = Product.objects.create(name='yaser', slugname='yaseeer', category=self.category_1, stock=50, price=10000, description='ashkjgdbakjshdb')

        self.order_1 = Order.objects.create(user=self.user, delivery_status='pending', delivery_date='2024-10-10', total_price=10000)
        self.order_2 = Order.objects.create(user=self.user, delivery_status='delivered', delivery_date='2024-10-01', total_price=10000)

    def test_create_order(self):
        url = reverse('order-create')  
        data = {
            'user': self.user.id,
            'delivery_status': 'pending',
            'delivery_date': '2024-11-01',
            'delivery_address': '123 Main St',
            'order_items': [  
                {
                    'product': self.product_1.id,
                    'quantity': 2 
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 3)  
        self.assertEqual(OrderItem.objects.count(), 1) 

    def test_retrieve_order(self):
        url = reverse('order-detail', kwargs={'pk': self.order_1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['delivery_status'], self.order_1.delivery_status)
        self.assertEqual(len(response.data['order_items']), 0) 

    def test_update_order(self):
        url = reverse('order-detail', kwargs={'pk': self.order_1.id})
        data = {'delivery_status': 'shipped'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order_1.refresh_from_db()
        self.assertEqual(self.order_1.delivery_status, 'shipped')

    def test_delete_order(self):
        url = reverse('order-detail', kwargs={'pk': self.order_1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 1) 

    def test_list_orders(self):
        url = reverse('order-list')
        response = self.client.get(url, {'deliveryStatus': 'pending', 'sort': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_pagination(self):
        url = reverse('order-list')
        response = self.client.get(url, {'page': 1, 'page_size': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


 


    def test_add_to_cart(self):
        url = reverse('add-to-cart')  
        data = {
            'product_id': self.product_1.id,
            'quantity': 3  
        }

        Cart.objects.filter(user=self.user).delete() 
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.product.id, self.product_1.id)
        self.assertEqual(cart_item.quantity, 3)  


    def test_retrieve_cart_item(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product_1, quantity=2)

        url = reverse('cart-item', kwargs={'product_id': self.product_1.id})
        response = self.client.get(url)


        self.assertEqual(response.status_code, status.HTTP_200_OK)

 
        items = response.data['items']
        

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['product']['id'], self.product_1.id)  
        self.assertEqual(items[0]['quantity'], 2)  


    def test_update_cart_item(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product_1, quantity=2)

        url = reverse('cart-item', kwargs={'product_id': self.product_1.id})
        data = {'quantity': 5}

        response = self.client.put(url, data, format='json')
        print(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_delete_cart_item(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product_1, quantity=2)

        url = reverse('cart-item', kwargs={'product_id': self.product_1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)  

    def test_cart_item_not_found(self):
        url = reverse('cart-item', kwargs={'product_id': self.product_1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)