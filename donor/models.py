import uuid
from datetime import timedelta
from random import randint
import string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
import random
from hospital.models import BloodDonationCampSchedule


class UserManager(BaseUserManager):
    def create_user(self, username, email, otp=None, is_organ_donor=False, is_blood_donor=False, blood_type=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        if otp is None:
            otp = str(randint(100000, 999999))  # Random 6-digit OTP
        user = self.model(
            username=username,
            email=email,
            otp=otp,
            otp_generated_at=timezone.now(),
            is_organ_donor=is_organ_donor,
            is_blood_donor=is_blood_donor,
            blood_type=blood_type,
            **extra_fields
        )
        user.set_unusable_password()  # Ensures no password is required
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, otp=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, otp, **extra_fields)

def generate_unique_id():
    """Generate a 6-character unique alphanumeric ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class User(AbstractBaseUser):
    unique_id = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
        default=generate_unique_id  # Automatically generate on user creation
    )    # Automatically generates a unique UUID
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, blank=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Initially set to inactive
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_organ_donor = models.BooleanField()
    is_blood_donor = models.BooleanField()
    blood_type = models.CharField(max_length=3)  # E.g., A+, O-

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.unique_id})"

    def save(self, *args, **kwargs):
        # Ensure password is not saved
        if not self.pk and self.password:
            self.set_unusable_password()
        super(User, self).save(*args, **kwargs)

    def is_otp_expired(self):
        """ Check if the OTP has expired (5 minutes window). """
        if not self.otp_generated_at:
            return True  # No OTP generated yet
        return timezone.now() > self.otp_generated_at + timezone.timedelta(minutes=5)

    def regenerate_otp(self):
        """ Regenerate OTP and update timestamp. """
        self.otp = str(randint(100000, 999999))
        self.otp_generated_at = timezone.now()
        self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    contact_number = models.IntegerField(null=False, blank=False)
    address = models.TextField(blank=False, null=False)
    id_proof = models.FileField(upload_to='id_proofs/', blank=False, null=False)  # File upload for ID proof
    willing_to_donate_organ = models.BooleanField()
    blood_group = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ])
    organs_to_donate = models.JSONField(
        blank=True,
        null=True,
        help_text="List of organs the user is willing to donate (e.g., ['Kidney', 'Heart'])."
    )
    willing_to_donate_blood = models.BooleanField(
        default=False,
        help_text="Indicates if the user is willing to donate blood."
    )

    def __str__(self):
        return f"Profile of {self.user.username},{self.blood_group}"

    def get_email(self):
        """Return the email of the associated user."""
        return self.user.email

User = get_user_model()

class BloodDonationSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donation_schedules", null=True, blank=True)
    date = models.DateField(help_text="Date of the scheduled donation")
    location = models.CharField(max_length=255, help_text="Location of the blood donation")
    is_available = models.BooleanField(default=True, help_text="Indicates if the user is available for donation")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The time when the donation schedule was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="The time when the donation schedule was last updated")

    def __str__(self):
        return f"Blood Donation for {self.user.username if self.user else 'Anonymous'} on {self.date}"

    class Meta:
        ordering = ['date']  # Ensures that schedules are ordered by date

class BloodDonationRegistration(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    camp = models.ForeignKey(BloodDonationCampSchedule, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)  # Automatically set the registration date when a record is created

    def __str__(self):
        return f"{self.user.username} registered for {self.camp.location} on {self.registration_date}"
