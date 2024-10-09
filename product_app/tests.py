from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_app.models import User
from .models import *
from .serializers import *
from django.utils.translation import activate
from parler.utils.context import switch_language

class CategoryTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Use force_authenticate or token, not both
        self.category = Category.objects.create(name='Test Category', slugname='test-caRtegory')
        self.create_url = reverse('create-category')
        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', kwargs={'category_id': self.category.id})

    def test_create_category(self):
        data = {'translations': {
                'en': {
                    'name': 'newcategory',
                },
                'fa': {
                    'name': 'کتگوری',
                }
            }, 'slugname': 'nAew-category'}
        response = self.client.post(self.create_url, data, format='json')  # Removed token since user is authenticated
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(id=response.data['data']['translations']['en']).name, 'newcategory')

    def test_list_categories(self):
        response = self.client.get(self.list_url, format='json')  # Removed token
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

        results = response.data['results'] if 'results' in response.data else response.data

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], self.category.name)

    def test_retrieve_category(self):
        response = self.client.get(self.detail_url, format='json') 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['translations']['en']['name'], self.category.name)

    def test_update_category(self):
        data = {'translations': {
                'en': {
                    'name': 'Updated Category',
                },
                'fa': {
                    'name': ' جدیدکتگوری',
                }
            }, 'slugname': 'updatedaaaacategory'}
        response = self.client.put(self.detail_url, data, format='json')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.data['translations']['en'], 'Updated Category')

    def test_delete_category(self):
        response = self.client.delete(self.detail_url, format='json')  
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

class SubcategoryTestCase(APITestCase):
    def setUp(self):
        activate('en')  # Activate the default language

        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create category with 'en' translation
        self.category = Category.objects.create(slugname="electronsics")
        self.category.set_current_language('en')
        self.category.name = 'Electronics'
        self.category.save()

        # Create subcategory and set translations in 'en' and 'fr'
        self.subcategory = Subcategory.objects.create(category=self.category,slugname="electronics")
        self.subcategory.set_current_language('en')
        self.subcategory.name = 'Mobile Phones'
        self.subcategory.save()

     
        self.subcategory.set_current_language('fa')
        self.subcategory.name = 'تلفن های همراه'
        
        self.subcategory.save()

    def test_create_subcategory(self):
        url = reverse('create-subcategory')
        data = {
            "slugname":"yaserrrsdfssssarrrrrrr",
            'translations': {
                'en': {
                    'name': 'Laptops',
                },
                'fa': {
                    'name': 'لپتاپ‌ها',
                }
            },
            'category': self.category.id
            
        }
        response = self.client.post(url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subcategory.objects.count(), 2)
        self.assertEqual(Subcategory.objects.latest('id').safe_translation_getter('name', any_language=True), 'Laptops')

    def test_retrieve_subcategory_in_english(self):
        url = reverse('subcategory-detail', args=[self.subcategory.id])
        response = self.client.get(url ) 
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        subcategory = response.json()
        print(subcategory)  # Log the response for debugging

        self.assertIn('translations', subcategory)
        #self.assertIn('en', subcategory['translations'])  # Check for 'en' language translation
        self.assertEqual(subcategory['translations']['en']['name'], 'Mobile Phones')  



    def test_retrieve_subcategory_in_farsi(self):
        # Add translation in Farsi for subcategory
        with switch_language(self.subcategory, 'fa'):
            self.subcategory.name = 'گوشی‌های موبایل'
            self.subcategory.save()

        url = reverse('subcategory-detail', args=[self.subcategory.id])
        response = self.client.get(url + "?language=fa")  # Retrieve in 'fa'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subcategory = response.json()
        self.assertIn('translations', subcategory)
        self.assertIn('fa', subcategory['translations'])
        self.assertEqual(subcategory['translations']['fa']['name'], 'گوشی‌های موبایل')

    def test_update_subcategory(self):
        url = reverse('subcategory-detail', args=[self.subcategory.id])
        data = {
            "slugname":"yaserrsssssrrrrfghfrrrrr",
            'translations': {
                
                'en': {
                    'name': 'Smartphones',
                },
                'fa': {
                    'name': 'تلفن‌های هوشمند',
                }
            },
            'category': self.category.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subcategory.refresh_from_db()

        # Validate the updated translations in both languages
        self.assertEqual(self.subcategory.safe_translation_getter('name', language_code='en'), 'Smartphones')
        self.assertEqual(self.subcategory.safe_translation_getter('name', language_code='fa'), 'تلفن‌های هوشمند')

    def test_delete_subcategory(self):
        url = reverse('subcategory-detail', args=[self.subcategory.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subcategory.objects.count(), 0)

class ProductTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Electronics', slugname='electronics')
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

    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product(self):
        url = reverse('create-product')

    # Create mock image files for testing
   
    # Prepare the flattened data
        data = {
        'translations_en_name': 'galaxy',
        'translations_en_description': 'Latest Samsung model',
        'translations_fa_name': 'گلکسی',
        'translations_fa_description': 'مدل جدید سامسونگ',
        'slugname': 'Galaxy',
        'price': 900,
        'stock': 15,
        'category': self.category.id,
        'brand': 'sony',
        }
    
        response = self.client.post(url, data, format='multipart')

        print(response.content)  # Useful for debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)  # Adjust this if you expect more/less
        self.assertEqual(Product.objects.latest('id').safe_translation_getter('name', any_language=True), 'galaxy')


    def test_retrieve_product(self):
        url = reverse('product-detail', kwargs={'product_id': self.product.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['translations']['en']['name'], 'iPhone')

    def test_update_product(self):
        url = reverse('product-detail', kwargs={'product_id': self.product.id})
        data = {
            'translations': {
                'en': {
                    'name': 'iPhone Updated',
                },
                'fa': {
                    'name': 'گلکسی',
                }},
            'slugname': 'iPhone',
            'description': 'Updated iPhone model',
            'price': 1000,
            'stock': 5,
            'category': self.category.id,
            'subcategory': self.subcategory.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(Product.objects.latest('id').safe_translation_getter('name', any_language=True), 'iPhone Updated')
        self.assertEqual(self.product.price, 1000)

    def test_delete_product(self):
        url = reverse('product-detail', kwargs={'product_id': self.product.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

class CommentTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Electronics', slugname='electronicls')
        self.product = Product.objects.create(
            name='iPhone',
            slugname='iPhone',
            description='Latest iPhone model',
            price=2000,
            stock=10,
            category=self.category
        )
        self.comment = Comment.objects.create(
            owner=self.user,
            product=self.product,
            text='Great product!'
           
        )

    def test_create_comment(self):
        url = reverse('create-comment')
        data = {
            'text': 'Amazing phone!',
            'product': self.product.id
            
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().text, 'Amazing phone!')

    def test_retrieve_comments(self):
        url = reverse('comment-list', kwargs={'product_id': self.product.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_comment(self):
        url = reverse('comment-detail', kwargs={'comment_id': self.comment.id})
        data = {
            'text': 'Updated comment text'
            
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Updated comment text')
        

    def test_delete_comment(self):
        url = reverse('comment-detail', kwargs={ 'comment_id': self.comment.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

class RatingAPITestCase(APITestCase):

    def setUp(self):
        
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

       
        self.category1 = Category.objects.create(name='category1', slugname='category1')
        self.category2 = Category.objects.create(name='category2', slugname='category2')

       
        self.product1 = Product.objects.create(name='Product 1', slugname='product1', description='Description 1', price=10.0, category=self.category1)
        self.product2 = Product.objects.create(name='Product 2', slugname='product2', description='Description 2', price=20.0, category=self.category2)

       
        self.rating1 = Rating.objects.create(product=self.product1, user=self.user1, rating=5)
        self.rating2 = Rating.objects.create(product=self.product2, user=self.user2, rating=4)

        
        self.create_url = reverse('create-rating')
        self.list_url = reverse('rating-list')
        self.detail_url = reverse('rating-detail', kwargs={'rating_id': self.rating1.pk})

       
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.token = RefreshToken.for_user(self.user1).access_token

    def test_create_rating_success(self):
        data = {
            'product': self.product2.id,
            'rating': 5,
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 3) 
        self.assertEqual(Rating.objects.get(id=response.data['id']).rating, 5)

    def test_create_rating_already_rated(self):
        data = {
            'product': self.product1.id,
            'rating': 3,
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'You have already rated this product.')

    def test_create_rating_invalid_data(self):
        data = {
            'product': self.product1.id,
            'rating': 6,  
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_ratings(self):
        url = reverse('rating-list')  
        response = self.client.get(url, format='json')
        results = response.data.get('results', response.data)  

        
        serializer = RatingSerializer(Rating.objects.all(), many=True)
        self.assertEqual(results, serializer.data)

    def test_filter_ratings_by_product(self):
        url = reverse('rating-list')  

        
        response = self.client.get(url, {'product': self.product1.id}, format='json')
        results = response.data.get('results', response.data)  

        
        serializer = RatingSerializer(Rating.objects.filter(product=self.product1), many=True)

        
        self.assertEqual(results, serializer.data)

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
        self.assertEqual(Rating.objects.count(), 1)  

    def test_retrieve_rating(self):
        response = self.client.get(self.detail_url)
        rating = Rating.objects.get(pk=self.rating1.pk)

       
        serializer = RatingSerializer(rating)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

class TopSellerAPITestCase(APITestCase):
    def setUp(self):
        activate('en')  

        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.category = Category.objects.create()
        self.category.set_current_language('en')
        self.category.name = 'Electronics'
        self.category.save()

        self.product_1 = Product.objects.create(category=self.category, stock=50, price=10000, sales_count=15)
        self.product_1.set_current_language('en')
        self.product_1.name = 'Product 1'
        self.product_1.description = 'Description of Product 1'
        self.product_1.save()
        
        self.product_2 = Product.objects.create(category=self.category, stock=30, price=20000, sales_count=25)
        self.product_2.set_current_language('en')
        self.product_2.name = 'Product 2'
        self.product_2.description = 'Description of Product 2'
        self.product_2.save()

        self.product_3 = Product.objects.create(category=self.category, stock=20, price=15000, sales_count=10)
        self.product_3.set_current_language('en')
        self.product_3.name = 'Product 3'
        self.product_3.description = 'Description of Product 3'
        self.product_3.save()

    def test_top_seller_products(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('top-seller')
      
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       
        self.assertLessEqual(len(response.data['results']), 10)
        
        products = response.json()['results']
        
        sorted_products = sorted([self.product_1, self.product_2, self.product_3], key=lambda x: x.sales_count, reverse=True)
        expected_ids = [product.id for product in sorted_products[:10]]
        

        self.assertListEqual([product['id'] for product in products], expected_ids)
     
        for product in products:
            self.assertIn('translations', product)
            self.assertIn('en', product['translations'])
            self.assertIn('name', product['translations']['en'])
            self.assertIn('description', product['translations']['en'])
            self.assertIn('category_name', product)
            self.assertIn('category', product)
            self.assertIn('brand', product)
            self.assertIn('price', product)
            self.assertIn('discount_percentage', product)
            self.assertIn('price_after_discount', product)
            self.assertIn('stock', product)
            self.assertIn('thumbnail', product)
            self.assertIn('created_at', product)
            self.assertIn('updated_at', product)
            self.assertIn('sales_count', product)
            self.assertIn('subcategory', product)