# Generated by Django 3.1 on 2021-06-03 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0026_auto_20210603_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='youtubelink',
            field=models.URLField(default=''),
        ),
    ]
