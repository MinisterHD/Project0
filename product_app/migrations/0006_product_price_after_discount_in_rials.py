# Generated by Django 5.1.2 on 2024-10-22 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0005_product_price_in_rials_alter_product_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price_after_discount_in_rials',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
