from django.urls import path
from .views import (
    CreateCategoryAPIView, CategoryListAPIView, CategoryAPIView,
    CreateSubcategoryAPIView, SubcategoryListAPIView, SubcategoryAPIView,
    ProductListAPIView, CreateProductAPIView, ProductAPIView,
    CommentListAPIView, CreateCommentAPIView, CommentAPIView,
    CreateRatingAPIView, RatingAPIView
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
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/create/', CreateProductAPIView.as_view(), name='create-product'),
    path('products/<int:product_id>/', ProductAPIView.as_view(), name='product-detail'),

    # Comment
    path('products/<int:product_id>/comments/', CommentListAPIView.as_view(), name='comment-list'),
    path('comments/create/', CreateCommentAPIView.as_view(), name='create-comment'),
    path('comments/<int:comment_id>/', CommentAPIView.as_view(), name='comment-detail'),

    # Rating
    path('ratings/create/', CreateRatingAPIView.as_view(), name='create-rating'),
    path('ratings/<int:rating_id>/', RatingAPIView.as_view(), name='rating-detail'),
]

    
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
