# Generated by Django 5.1.1 on 2025-01-09 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospital',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='hospital_images/'),
        ),
    ]
