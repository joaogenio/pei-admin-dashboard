# Generated by Django 3.2.5 on 2021-08-10 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0037_document_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentupdate',
            name='contentpage',
            field=models.IntegerField(default=0),
        ),
    ]
