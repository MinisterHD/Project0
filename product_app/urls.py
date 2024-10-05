from django.urls import path
from .views import (
    CreateCategoryAPIView, CategoryListAPIView, CategoryAPIView,
    CreateSubcategoryAPIView, SubcategoryListAPIView, SubcategoryAPIView,
    ProductListAPIView, CreateProductAPIView, ProductAPIView,
    CommentListAPIView, CreateCommentAPIView, CommentAPIView,
    CreateRatingAPIView, RatingAPIView,RatingListAPIView
)

urlpatterns = [
    # Category
    path('categories/create/', CreateCategoryAPIView.as_view(), name='create-category'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<int:category_id>/', CategoryAPIView.as_view(), name='category-detail'),

    # Subcategory
    path('subcategories/create/', CreateSubcategoryAPIView.as_view(), name='create-subcategory'),
    path('subcategories/', SubcategoryListAPIView.as_view(), name='subcategory-list'),
    path('subcategories/<int:subcategory_id>/', SubcategoryAPIView.as_view(), name='subcategory-detail'),

    # Product
    path('products/create/', CreateProductAPIView.as_view(), name='create-product'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:product_id>/', ProductAPIView.as_view(), name='product-detail'),

    # Comment
    path('comments/create/', CreateCommentAPIView.as_view(), name='create-comment'),
    path('products/<int:product_id>/comments/', CommentListAPIView.as_view(), name='comment-list'),
    path('comments/<int:comment_id>/', CommentAPIView.as_view(), name='comment-detail'),

    # Rating
    path('ratings/create/', CreateRatingAPIView.as_view(), name='create-rating'),
    path('ratings/', RatingListAPIView.as_view(), name='rating-list'),  
    path('ratings/<int:rating_id>/', RatingAPIView.as_view(), name='rating-detail'), 
]


