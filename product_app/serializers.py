from rest_framework import serializers
from .models import *
from django.core.files.storage import default_storage



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slugname',]

class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Subcategory
        fields = '__all__'  

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=True),
        write_only=True,
        required=False 
    )
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ["id", "created_at", "updated_at", "price_after_discount"]

    def create(self, validated_data):
        images = validated_data.pop('images', None)

        product = Product.objects.create(**validated_data)

        if images:
            image_urls = []
            for image in images:
                image_path = self.save_image(image)
                image_urls.append(image_path)

            product.images = image_urls

        product.save()
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if images:
            image_urls = []
            for image in images:
                image_path = self.save_image(image)
                image_urls.append(image_path)
            instance.images = image_urls

        instance.save()
        return instance

    def save_image(self, image):
        return default_storage.save(f'products/images/{image.name}', image) 

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' 

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields   = ('id', 'owner', 'text', 'created_at',"product")
        read_only_fields = ['id', 'created_at']

class RatingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__' 
        read_only_fields = ['user', 'created_at']

class RatingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__' 
        read_only_fields = ['user', 'created_at','product']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'  

