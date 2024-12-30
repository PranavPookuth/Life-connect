# Generated by Django 5.1.1 on 2024-12-06 05:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0004_delete_appnotifications'),
        ('hospital', '0002_emergencydonationalert'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonorResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_status', models.CharField(choices=[('confirmed', 'Confirmed'), ('declined', 'Declined'), ('pending', 'Pending')], default='pending', max_length=10)),
                ('message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('donor_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='donor.userprofile')),
                ('emergency_alert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital.emergencydonationalert')),
            ],
        ),
    ]