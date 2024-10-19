from django.urls import path, include
from .views import (
    CategoryViewSet,SubcategoryViewSet,
    ProductViewSet,
    CommentViewSet,
    RatingViewSet,TopSellerAPIView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubcategoryViewSet, basename='subcategory')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'ratings', RatingViewSet, basename='rating')

urlpatterns = [
    # Category
    #path('categories/create/', CreateCategoryAPIView.as_view(), name='create-category'),
    #path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    #path('categories/<int:category_id>/', CategoryAPIView.as_view(), name='category-detail'),
    path('', include(router.urls)),

    # Subcategory
    #path('subcategories/create/', CreateSubcategoryAPIView.as_view(), name='create-subcategory'),
    #path('subcategories/', SubcategoryListAPIView.as_view(), name='subcategory-list'),
    #path('subcategories/<int:subcategory_id>/', SubcategoryAPIView.as_view(), name='subcategory-detail'),
    path('', include(router.urls)),

    # Product
    #path('products/create/', CreateProductAPIView.as_view(), name='create-product'),
    #path('products/', ProductListAPIView.as_view(), name='product-list'),
    #path('products/<int:product_id>/', ProductAPIView.as_view(), name='product-detail'),
    path('', include(router.urls)),
    
    # Comment
    #path('comments/create/', CreateCommentAPIView.as_view(), name='create-comment'),
    #path('products/<int:product_id>/comments/', CommentListAPIView.as_view(), name='comment-list'),
    #path('comments/<int:comment_id>/', CommentAPIView.as_view(), name='comment-detail'),
    path('', include(router.urls)),
    
    # Rating
    #path('ratings/create/', CreateRatingAPIView.as_view(), name='create-rating'),
    #path('ratings/', RatingListAPIView.as_view(), name='rating-list'),  
    #path('ratings/<int:rating_id>/', RatingAPIView.as_view(), name='rating-detail'), 
    path('', include(router.urls)), 
    
    #TopSellerList
    path('products/top-seller/', TopSellerAPIView.as_view(), name='top-seller'),



 
]



