# Generated by Django 3.1 on 2021-05-14 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20210513_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentupdate',
            name='contentname',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]