# Generated by Django 3.2.8 on 2021-10-20 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0050_auto_20211018_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='ytlink',
            name='duration',
            field=models.PositiveIntegerField(default=10),
        ),
    ]