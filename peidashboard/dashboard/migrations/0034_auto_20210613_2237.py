# Generated by Django 3.1 on 2021-06-13 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_agentupdate_url_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentupdate',
            name='url_hash',
            field=models.CharField(default=0, max_length=32, unique=True),
            preserve_default=False,
        ),
    ]