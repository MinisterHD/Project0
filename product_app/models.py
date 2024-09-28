from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slugname = models.SlugField(max_length=255, unique=True)

class Subcategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slugname = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', blank=True) 
    product_descriptions=models.TextField(max_length=500,blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



    

