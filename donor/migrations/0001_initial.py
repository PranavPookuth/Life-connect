# Generated by Django 5.1.1 on 2024-12-04 09:14

import django.db.models.deletion
import donor.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('unique_id', models.CharField(default=donor.models.generate_unique_id, editable=False, max_length=6, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=255)),
                ('otp', models.CharField(blank=True, max_length=6, null=True)),
                ('otp_generated_at', models.DateTimeField(blank=True, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_organ_donor', models.BooleanField()),
                ('is_blood_donor', models.BooleanField()),
                ('blood_type', models.CharField(max_length=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BloodDonationSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Date of the scheduled donation')),
                ('location', models.CharField(help_text='Location of the blood donation', max_length=255)),
                ('is_available', models.BooleanField(default=True, help_text='Indicates if the user is available for donation')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The time when the donation schedule was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The time when the donation schedule was last updated')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donation_schedules', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_number', models.IntegerField()),
                ('address', models.TextField()),
                ('id_proof', models.FileField(upload_to='id_proofs/')),
                ('willing_to_donate_organ', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=3)),
                ('organs_to_donate', models.JSONField(blank=True, help_text="List of organs the user is willing to donate (e.g., ['Kidney', 'Heart']).", null=True)),
                ('willing_to_donate_blood', models.BooleanField(default=False, help_text='Indicates if the user is willing to donate blood.')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BloodDonationRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('camp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital.blooddonationcampschedule')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='donor.userprofile')),
            ],
        ),
    ]
