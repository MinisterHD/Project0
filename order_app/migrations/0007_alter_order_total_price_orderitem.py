# Generated by Django 5.1.1 on 2024-10-06 09:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0006_alter_order_total_price'),
        ('product_app', '0004_product_sales_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='order_app.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.product')),
            ],
        ),
    ]