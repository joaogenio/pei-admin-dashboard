# Generated by Django 3.1 on 2021-05-14 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_agentupdate_contentname'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='docname',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
