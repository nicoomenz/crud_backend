# Generated by Django 5.1.5 on 2025-04-24 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_paymentcombo_precio_credito_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='custom_products',
        ),
        migrations.AddField(
            model_name='paymentcombo',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='paymentproduct',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
