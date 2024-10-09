from rest_framework import serializers
from .models import *
from django.core.files.storage import default_storage
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = ['id', 'translations','slugname']  

class SubcategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Subcategory)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Subcategory
        fields = ['id', 'translations','category','category_name','slugname'] 
    def get_translations(self, obj):
            return {
                lang: {
                 'name': obj.safe_translation_getter('name', language_code=lang)
                }
                 for lang in obj.get_available_languages()   }


class ProductSerializer(TranslatableModelSerializer):
    translations_en_name = serializers.CharField(write_only=True, required=True)
    translations_en_description = serializers.CharField(write_only=True, required=True)
    translations_fa_name = serializers.CharField(write_only=True, required=True)
    translations_fa_description = serializers.CharField(write_only=True, required=True)

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

 
        product = Product.objects.create(
            brand=validated_data.pop('brand'),
            slugname=validated_data.pop('slugname'),
            price=validated_data.pop('price'),
            stock=validated_data.pop('stock'),
            category=validated_data.pop('category'),
            subcategory=validated_data.pop('subcategory', None)
        )

 
        translations = {
            'en': {
                'name': validated_data.pop('translations_en_name'),
                'description': validated_data.pop('translations_en_description'),
            },
            'fa': {
                'name': validated_data.pop('translations_fa_name'),
                'description': validated_data.pop('translations_fa_description'),
            },
        }

        for lang, translation in translations.items():
            product.set_current_language(lang)
            product.name = translation['name']
            product.description = translation['description']
            product.save_translations()

 
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

    
        translations = {
            'en': {
                'name': validated_data.pop('translations_en_name', instance.safe_translation_getter('name', language='en')),
                'description': validated_data.pop('translations_en_description', instance.safe_translation_getter('description', language='en')),
            },
            'fa': {
                'name': validated_data.pop('translations_fa_name', instance.safe_translation_getter('name', language='fa')),
                'description': validated_data.pop('translations_fa_description', instance.safe_translation_getter('description', language='fa')),
            },
        }

        for lang, translation in translations.items():
            instance.set_current_language(lang)
            instance.name = translation['name']
            instance.description = translation['description']
            instance.save_translations()

      
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


class ProductDetailSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
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

