# Generated by Django 5.1.1 on 2024-10-05 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0005_alter_order_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.IntegerField(default=0),
        ),
    ]
