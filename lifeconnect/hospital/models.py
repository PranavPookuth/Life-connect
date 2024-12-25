from django.db import models
from random import randint
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

    def regenerate_otp(self):
        """Generate a new OTP and update timestamp."""
        self.otp = str(randint(100000, 999999))  # Generate a 6-digit OTP
        self.otp_generated_at = timezone.now()
        self.save()

    def is_otp_expired(self):
        """Check if the OTP has expired (5-minute window)."""
        if not self.otp_generated_at:
            return True  # OTP not generated yet
        expiration_time = self.otp_generated_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time

class BloodDonationCampSchedule(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
     ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)  # Hospital hosting the camp
    date = models.DateField()  # Date of the blood donation camp
    location = models.CharField(max_length=255)  # Location of the blood donation camp
    start_time = models.TimeField()  # Start time for the camp
    end_time = models.TimeField()  # End time for the camp
    description = models.TextField(blank=True, null=True)  # Description of the camp
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')  # Status of the camp
    created_at = models.DateTimeField(aut o_now_add=True)  # Automatically set when the camp is created

    def __str__(self):
        return f"Blood Donation Camp at {self.hospital.name} on {self.date} ({self.status})"

class EmergencyDonationAlert(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE)  # Requesting hospital
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)  # Required blood group
    organ_required = models.CharField(max_length=100, blank=True, null=True)  # E.g., Kidney, Liver
    location = models.CharField(max_length=255)  # Location of the hospital or emergency site
    message = models.TextField(blank=True, null=True)  # Additional details about the request
    created_at = models.DateTimeField(auto_now_add=True)  # Request creation time
    is_active = models.BooleanField(default=True)  # Whether the alert is still valid

    def __str__(self):
        return f"Emergency Alert: {self.blood_group} at {self.hospital.name}"






