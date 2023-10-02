# Generated by Django 4.2.3 on 2023-10-01 09:06

from django.db import migrations, models
import supplement_store.models


class Migration(migrations.Migration):

    dependencies = [
        ('supplement_store', '0020_alter_item_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image1',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=supplement_store.models.item_image_upload_path),
        ),
        migrations.AlterField(
            model_name='item',
            name='image2',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=supplement_store.models.item_image_upload_path),
        ),
        migrations.AlterField(
            model_name='item',
            name='image3',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=supplement_store.models.item_image_upload_path),
        ),
        migrations.AlterField(
            model_name='item',
            name='main_image',
            field=models.ImageField(max_length=255, upload_to=supplement_store.models.item_image_upload_path),
        ),
        migrations.AlterField(
            model_name='slideshowimage',
            name='image',
            field=models.ImageField(max_length=255, upload_to=supplement_store.models.slide_show_upload_path),
        ),
    ]