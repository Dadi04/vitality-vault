# Generated by Django 5.1.6 on 2025-03-12 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplement_store', '0042_remove_item_color_remove_item_gender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.CharField(choices=[('IronMaxx', 'IronMaxx'), ('OstroVit', 'OstroVit'), ('BioTechUSA', 'BioTechUSA'), ('AmiX', 'AmiX'), ('Myprotein', 'Myprotein'), ('BSN', 'BSN'), ('Optimum Nutrition', 'Optimum Nutrition'), ('Scitec Nutrition', 'Scitec Nutrition'), ('Gorilla Mind', 'Gorilla Mind'), ('HTLT', 'HTLT'), ('Quest Nutrition', 'Quest Nutrition')]),
        ),
    ]
