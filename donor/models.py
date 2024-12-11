import uuid
from datetime import timedelta
from random import randint
import string
from django.contrib.auth import get_user_model
import random
from hospital.models import BloodDonationCampSchedule,EmergencyDonationAlert,Hospital
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

def generate_unique_id():
    """Generate a 6-character unique alphanumeric ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class UserManager(BaseUserManager):
    def create_user(self, username, email, blood_type, is_blood_donor=False, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        if not blood_type:
            raise ValueError('The Blood Type field must be set')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            blood_type=blood_type,
            is_blood_donor=is_blood_donor,
            **extra_fields
        )
        user.set_unusable_password()  # Ensures no password is required
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, blood_type=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, blood_type, **extra_fields)

class User(AbstractBaseUser):
    unique_id = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
        default=generate_unique_id  # Automatically generate on user creation
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, blank=False, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Initially set to inactive
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_blood_donor = models.BooleanField(default=False)
    blood_type = models.CharField(max_length=3)  # E.g., A+, O-
    created_at = models.DateTimeField(auto_now_add=True)

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
        """Check if the OTP has expired (5 minutes window)."""
        if not self.otp_generated_at:
            return True  # No OTP generated yet
        return timezone.now() > self.otp_generated_at + timezone.timedelta(minutes=5)

    def regenerate_otp(self):
        """Regenerate OTP and update timestamp."""
        self.otp = str(random.randint(100000, 999999))
        self.otp_generated_at = timezone.now()
        self.save()

#Creating Donor Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    contact_number = models.IntegerField(null=False, blank=False)
    address = models.TextField(blank=False, null=False)
    id_proof = models.FileField(upload_to='id_proofs/', blank=False, null=False)  # File upload for ID proof
    willing_to_donate_organ = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
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
#User Scheduling Blood Donation Camp
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

#User Registering For Blood Donation Camp
class BloodDonationRegistration(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    camp = models.ForeignKey(BloodDonationCampSchedule, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)  # Automatically set the registration date when a record is created
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} registered for {self.camp.location} on {self.registration_date}"

#User responding For
class DonorResponse(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # The responding user
    alert = models.ForeignKey(EmergencyDonationAlert, on_delete=models.CASCADE, related_name='responses')
    response_message = models.TextField(blank=True, null=True)  # Optional message from the user
    responded_at = models.DateTimeField(auto_now_add=True)  # Timestamp of response
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.user.username} responded to Alert {self.alert.id}"

User = get_user_model()
class ChatMessage(models.Model):
    SENDER_TYPE_CHOICES = [
        ('donor', 'Donor'),
        ('hospital', 'Hospital'),
    ]

    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_TYPE_CHOICES,
        help_text="Indicates whether the sender is a donor or hospital.",
    )
    sender_name = models.CharField(
        max_length=255,
        help_text="Name of the sender (donor or hospital).",
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        help_text="The hospital involved in the chat.",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender_type} ({self.sender_name}): {self.content[:20]}"

    class Meta:
        ordering = ['-timestamp']


