# Generated by Django 3.2.18 on 2023-02-26 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0055_alter_agentupdate_agent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentprogram',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
