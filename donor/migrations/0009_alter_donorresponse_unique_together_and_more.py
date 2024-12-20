# Generated by Django 5.1.1 on 2024-12-06 11:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0008_donorresponse'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='donorresponse',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='donorresponse',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='donorresponse',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]
