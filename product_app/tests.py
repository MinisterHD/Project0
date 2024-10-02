from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_app.models import User
from .models import *
from .serializers import *


class CategoryTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Test Category', slugname='test-category')
        self.create_url = reverse('create-category')
        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', kwargs={'category_id': self.category.id})
        self.token = RefreshToken.for_user(self.user).access_token

    def test_create_category(self):
        data = {'name': 'New Category', 'slugname': 'new-category'}
        response = self.client.post(self.create_url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(id=response.data['data']['id']).name, 'New Category')

    def test_list_categories(self):
        response = self.client.get(self.list_url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.category.name)

    def test_retrieve_category(self):
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)

    def test_update_category(self):
        data = {'name': 'Updated Category', 'slugname': 'updated-category'}
        response = self.client.put(self.detail_url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_delete_category(self):
        response = self.client.delete(self.detail_url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)


class SubcategoryTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category, slugname='slug-for-test')
        self.client.force_authenticate(user=self.user)
        self.token = RefreshToken.for_user(self.user).access_token

    def test_create_subcategory(self):
        url = reverse('create-subcategory')
        data = {
            'name': 'New Subcategory',
            'slugname': 'new-slugname',
            'category': self.category.id
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subcategory.objects.count(), 2)
        self.assertEqual(Subcategory.objects.get(id=response.data['data']['id']).name, 'New Subcategory')


    def test_list_subcategories(self):
        url = reverse('subcategory-list')
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.subcategory.name)

    def test_list_subcategories_filtered_by_category(self):
        url = reverse('subcategory-list')
        response = self.client.get(url, {'category': self.category.id}, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.subcategory.name)

    def test_retrieve_subcategory(self):
        url = reverse('subcategory-detail', kwargs={'subcategory_id': self.subcategory.id})
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.subcategory.name)

    def test_update_subcategory(self):
        url = reverse('subcategory-detail', kwargs={'subcategory_id': self.subcategory.id})
        data = {
            'name': 'Updated Subcategory',
            'category': self.category.id,
           'slugname': 'updated-subcategory-slug'  
        }
        response = self.client.put(url, data,  HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slugname'], 'updated-subcategory-slug')


    def test_delete_subcategory(self):
        url = reverse('subcategory-detail', kwargs={'subcategory_id': self.subcategory.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subcategory.objects.count(), 0)


class ProductTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Electronics',slugname='electronics')
        self.subcategory = Subcategory.objects.create(name='Mobile Phones', category=self.category)
        self.product = Product.objects.create(
            name='iPhone',
            slugname='iPhone',
            brand='sony',
            description='Latest iPhone model',
            price=2000,
            stock=10,
            category=self.category,
            subcategory=self.subcategory
             )
        self.client.force_authenticate(user=self.user)
        self.token = RefreshToken.for_user(self.user).access_token

    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        

    def test_create_product(self):
        url = reverse('create-product')
        data = {
            'name': 'Samsung Galaxy',
            'slugname':'Galaxy',
            'description': 'Latest Samsung model',
            'price': 900,
            'stock': 15,
            'category': self.category.id,
            'brand':'sony',
            'subcategory': self.subcategory.id
        
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.get(name='Samsung Galaxy').description, 'Latest Samsung model')

    def test_retrieve_product(self):
        url = reverse('product-detail', kwargs={'product_id': self.product.id})
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'iPhone')

    def test_update_product(self):
        url = reverse('product-detail', kwargs={'product_id': self.product.id})
        data = {
            'name': 'iPhone Updated',
            'slugname':'iPhone',
            'description': 'Updated iPhone model',
            'price': 1000,
            'stock': 5,
            'category': self.category.id,
            'subcategory': self.subcategory.id
        }
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'iPhone Updated')
        self.assertEqual(self.product.price, 1000)

    def test_delete_product(self):
        url = reverse('product-detail', kwargs={'product_id': self.product.id})
        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)


class CommentTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='testuser', password='testpassword')
        samplecategory = Category.objects.create(name='Test Category', slugname='test-category')
        self.product = Product.objects.create(name='Test Product',price=10000,stock=5,category=samplecategory)
        self.comment = Comment.objects.create(product=self.product, owner=self.owner, text='Test comment')
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)
        self.token = RefreshToken.for_user(self.owner).access_token

    def test_comment_list(self):
        url = reverse('comment-list', kwargs={'product_id': self.product.id})
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_comment(self):
        url = reverse('create-comment')
        data = {'product': self.product.id, 'text': 'New comment', 'owner': self.owner.id}
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
    

    def test_retrieve_comment(self):
        url = reverse('comment-detail', kwargs={'comment_id': self.comment.id})
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], self.comment.text)

    def test_update_comment(self):
        url = reverse('comment-detail', kwargs={'comment_id': self.comment.id})
        data = {'product': self.product.id,'text': 'Updated comment', 'owner': self.owner.id}
        response = self.client.put(url, data, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Updated comment')
        

    def test_delete_comment(self):
        url = reverse('comment-detail', kwargs={'comment_id': self.comment.id})
        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Bearer {self.token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)


class RatingAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

        self.category1=Category.objects.create(name='category1',slugname='category1')
        self.category2=Category.objects.create(name='category2',slugname='category2')

    
        self.product1 = Product.objects.create(name='Product 1',slugname='product1', description='Description 1', price=10.0,category=self.category1)
        self.product2 = Product.objects.create(name='Product 2',slugname='product2', description='Description 2', price=20.0,category=self.category2)

      
        self.rating1 = Rating.objects.create(product=self.product1, user=self.user1, rating=5)
        self.rating2 = Rating.objects.create(product=self.product2, user=self.user2, rating=4)
        self.rating3 = Rating.objects.create(product=self.product1, user=self.user2, rating=3)

   
        self.create_url = reverse('create-rating')
        self.list_url = reverse('rating-list')
        self.detail_url = reverse('rating-detail', kwargs={'rating_id': self.rating1.pk})

   
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.token = RefreshToken.for_user(self.user1).access_token

    def test_create_rating(self):
        data = {
            'product': self.product1.id,
            'rating': 5,
           
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 4)
        self.assertEqual(Rating.objects.get(id=response.data['id']).rating, 5)

    def test_create_rating_invalid_data(self):
        data = {
            'product': self.product1.id,
            'rating': 6,
            
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_ratings(self):
        response = self.client.get(self.list_url)
        ratings = Rating.objects.all()
        serializer = RatingSerializer(ratings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_ratings_by_product(self):
        response = self.client.get(self.list_url, {'product': self.product1.id})
        ratings = Rating.objects.filter(product=self.product1)
        serializer = RatingSerializer(ratings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_ratings_by_user(self):
        response = self.client.get(self.list_url, {'user': self.user1.id})
        ratings = Rating.objects.filter(user=self.user1)
        serializer = RatingSerializer(ratings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_ratings_by_product_and_user(self):
        response = self.client.get(self.list_url, {'product': self.product1.id, 'user': self.user2.id})
        ratings = Rating.objects.filter(product=self.product1, user=self.user2)
        serializer = RatingSerializer(ratings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_rating(self):
        response = self.client.get(self.detail_url)
        rating = Rating.objects.get(pk=self.rating1.pk)
        serializer = RatingSerializer(rating)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_rating(self):
        data = {
            'rating': 4,
            
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rating1.refresh_from_db()
        self.assertEqual(self.rating1.rating, 4)
        

    def test_delete_rating(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Rating.objects.count(), 2)
