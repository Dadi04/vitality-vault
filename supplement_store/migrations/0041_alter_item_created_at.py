# Generated by Django 5.1.6 on 2025-03-08 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplement_store', '0040_item_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
