# Generated by Django 5.1.1 on 2024-10-16 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0004_alter_wishlistitem_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipped_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
