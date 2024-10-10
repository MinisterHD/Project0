from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Product

@receiver(pre_save, sender=Product)
def calculate_price_after_discount(sender, instance, **kwargs):

    if instance.price and instance.discount_percentage:
        instance.price_after_discount = instance.price * (1 - (instance.discount_percentage / 100))
    else:
        instance.price_after_discount = instance.price  