# Generated by Django 5.1.6 on 2025-02-15 12:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplement_store', '0031_remove_transaction_is_purchased_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='is_on_sale',
        ),
    ]
