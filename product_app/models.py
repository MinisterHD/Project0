from django.db import models
from user_app.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True,null=False,blank=False)
    slugname = models.SlugField(max_length=255, unique=True,null=False,blank=False)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=255, unique=True,null=False,blank=False)
    slugname = models.SlugField(max_length=255, unique=True,null=False,blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=False,blank=False)

    def __str__(self):
        return self.name

class Rating(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'),
                                          (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.rating} by {self.user}'

class Product(models.Model):
    name = models.CharField(max_length=255,unique=True)
    slugname=models.SlugField(max_length=255,unique=True,default='default-slug')
    brand=models.CharField(max_length=50,default='No Brand',null=False,blank=False)
    description = models.TextField(max_length=2000)
    price = models.IntegerField(null=False, blank=False)
    discount_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],default=0)
    price_after_discount = models.IntegerField(null=True,blank=True)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True)
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True)
    product_descriptions = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        self.price_after_discount = self.price * (1 - (self.discount_percentage / 100))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments',null=False,blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=200,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.owner} on {self.product}'

@receiver(pre_save, sender=Product)
def calculate_price_after_discount(sender, instance, **kwargs):
    instance.price_after_discount = instance.price * (1 - (instance.discount_percentage / 100))
    
