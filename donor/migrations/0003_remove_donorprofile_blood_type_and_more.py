# Generated by Django 5.1.1 on 2024-11-29 09:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0002_donorprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donorprofile',
            name='blood_type',
        ),
        migrations.RemoveField(
            model_name='donorprofile',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='donorprofile',
            name='willing_to_donate',
        ),
        migrations.AddField(
            model_name='donorprofile',
            name='blood_group',
            field=models.CharField(default='A+', max_length=3),
        ),
        migrations.AddField(
            model_name='donorprofile',
            name='contact_number',
            field=models.CharField(default='0123456789', max_length=15),
        ),
        migrations.AlterField(
            model_name='donorprofile',
            name='address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='donorprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donor_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
