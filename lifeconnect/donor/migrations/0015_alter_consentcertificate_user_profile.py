# Generated by Django 5.1.1 on 2024-12-24 07:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0014_consentcertificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consentcertificate',
            name='user_profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='consent_certificate', to='donor.userprofile'),
        ),
    ]