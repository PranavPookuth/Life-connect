# Generated by Django 5.1.1 on 2024-11-30 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='next_available_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
