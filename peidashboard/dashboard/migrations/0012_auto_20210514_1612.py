# Generated by Django 3.1 on 2021-05-14 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_document_docname'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='viewcount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='document',
            name='viewtime',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
