# Generated by Django 3.1.7 on 2021-04-13 14:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20210407_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartproductm2m',
            name='product_count',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
