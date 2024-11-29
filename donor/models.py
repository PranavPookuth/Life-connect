import uuid
from random import randint
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

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
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, otp=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, otp, **extra_fields)

class User(AbstractBaseUser):
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
        return self.username

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
