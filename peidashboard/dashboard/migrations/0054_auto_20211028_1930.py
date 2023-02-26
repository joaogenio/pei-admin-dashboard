# Generated by Django 3.2.8 on 2021-10-28 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0053_alter_programentry_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='viewlink',
            field=models.URLField(default='', editable=False),
        ),
        migrations.AlterField(
            model_name='document',
            name='docfile',
            field=models.FileField(unique=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='ytlink',
            name='link',
            field=models.URLField(default='', unique=True),
        ),
    ]
