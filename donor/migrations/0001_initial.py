# Generated by Django 5.1.1 on 2024-11-30 06:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
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
                ('time', models.TimeField(help_text='Time of the scheduled donation')),
                ('location', models.CharField(help_text='Location of the blood donation', max_length=255)),
                ('is_available', models.BooleanField(help_text='Indicates if the user is available for donation', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donation_schedules', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_number', models.IntegerField()),
                ('address', models.TextField()),
                ('id_proof', models.FileField(upload_to='id_proofs/')),
                ('willing_to_donate_organ', models.BooleanField()),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=3)),
                ('organs_to_donate', models.JSONField(blank=True, help_text="List of organs the user is willing to donate (e.g., ['Kidney', 'Heart']).", null=True)),
                ('willing_to_donate_blood', models.BooleanField(default=False, help_text='Indicates if the user is willing to donate blood.')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
