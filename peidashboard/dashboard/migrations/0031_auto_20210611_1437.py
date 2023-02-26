# Generated by Django 3.1 on 2021-06-11 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0030_auto_20210610_1549'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agentupdate',
            name='contentname',
        ),
        migrations.AddField(
            model_name='agentupdate',
            name='content',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.document'),
        ),
        migrations.AlterField(
            model_name='agentupdate',
            name='contentid',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]