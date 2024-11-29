# Generated by Django 5.1.1 on 2024-11-29 10:13

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
    ]
