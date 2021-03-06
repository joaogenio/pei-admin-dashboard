# Generated by Django 3.1 on 2021-06-01 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_auto_20210601_1849'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.agent')),
                ('content', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.document')),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.person')),
            ],
        ),
    ]
