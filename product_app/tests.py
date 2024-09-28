from django.test import TestCase, Client
from django.urls import reverse
from product_app.models import Category, Subcategory, Product, Comment
from product_app.serializers import (
    CategorySerializer,
    SubcategorySerializer,
    ProductSerializer,
    CommentSerializer,
)
from product_app.views import (
    CreateCategoryAPIView,
    CategoryListAPIView,
    CategoryAPIView,
    CreateSubcategoryAPIView,
    SubcategoryListAPIView,
    SubcategoryAPIView,
    ProductListAPIView,
    CreateProductAPIView,
    ProductAPIView,
    CommentListAPIView,
    CreateCommentAPIView,
    CommentAPIView,
)


class YourAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create sample data for testing
        self.category = Category.objects.create(name="Test Category", slugname="test-category")
        self.subcategory = Subcategory.objects.create(name="Test Subcategory", category=self.category)
        self.product = Product.objects.create(name="Test Product", price=10.99, category=self.category, stock=10, subcategory=self.subcategory)

    def test_category_creation_with_valid_data(self):
        # Test creating a category with valid data
        data = {"name": "New Category", "slugname": "new-category"}
        response = self.client.post(
            reverse("category-create"), data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)  # Created
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data["name"], data["name"])

    def test_category_creation_with_missing_data(self):
        # Test creating a category with missing data
        data = {"name": "New Category"}
        response = self.client.post(
            reverse("category-create"), data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)  # Bad Request
        self.assertIn("This field is required.", response.content.decode())

    def test_category_list(self):
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(len(response.data), 1)  # One category in the list
        self.assertEqual(response.data[0]["name"], self.category.name)

        # Test filtering by slugname
        response = self.client.get(reverse("category-list") + "?slugname=test-category")
        self.assertEqual(response.data[0]["slugname"], "test-category")

    def test_category_detail(self):
        response = self.client.get(reverse("category-management", args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(response.data["name"], self.category.name)

    def test_subcategory_creation_with_valid_data(self):
        # Test creating a subcategory with valid data
        data = {"name": "New Subcategory", "category": self.category.pk}
        response = self.client.post(
            reverse("subcategory-create"), data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)  # Created
        self.assertEqual(Subcategory.objects.count(), 2)
        self.assertEqual(response.data["name"], data["name"])

    