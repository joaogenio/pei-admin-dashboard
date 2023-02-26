# Generated by Django 3.1 on 2021-06-02 20:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0024_person_descriptor'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentprogram',
            name='group',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='dashboard.agentgroup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='programentry',
            name='program',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='dashboard.contentprogram'),
            preserve_default=False,
        ),
    ]