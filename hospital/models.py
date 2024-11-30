from django.db import models
from random import randint
from django.utils import timezone

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

