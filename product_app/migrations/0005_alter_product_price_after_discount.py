# Generated by Django 5.1.1 on 2024-10-01 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0004_alter_product_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price_after_discount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
