# Generated by Django 3.1 on 2021-06-01 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_auto_20210601_1848'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agent',
            options={'ordering': ['group', 'id']},
        ),
    ]