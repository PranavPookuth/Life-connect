import django_filters
import pytz
from rest_framework import serializers, generics
from .models import *
from django.core.mail import send_mail
import random
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from donor.models import UserProfile, BloodDonationSchedule,UserConsent
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db.models import Count

class HospitalRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ['name', 'email', 'contact_number', 'address']

    def validate_email(self, value):
        if Hospital.objects.filter(email=value, is_verified=True).exists():
            raise serializers.ValidationError("Hospital with this email is already verified.")
        return value

    def validate_contact_number(self, value):
        if Hospital.objects.filter(contact_number=value).exists():
            raise serializers.ValidationError("Hospital with this contact number is already registered.")
        return value

    def create(self, validated_data):
        hospital = Hospital.objects.create(**validated_data)
        hospital.regenerate_otp()
        send_mail(
            'OTP Verification',
            f'Your OTP is {hospital.otp}',
            'praveencodeedex@gmail.com',
            [hospital.email]
        )
        return hospital

class HospitalOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            hospital = Hospital.objects.get(email=data['email'])

            if hospital.is_verified:
                raise serializers.ValidationError("This hospital is already verified.")

            if hospital.is_otp_expired():
                hospital.regenerate_otp()
                send_mail(
                    'OTP Expired - New OTP',
                    f'Your new OTP is {hospital.otp}',
                    'praveencodeedex@gmail.com',
                    [hospital.email]
                )
                raise serializers.ValidationError("OTP expired. A new OTP has been sent to your email.")

            if hospital.otp != data['otp']:
                raise serializers.ValidationError("Invalid OTP.")

        except Hospital.DoesNotExist:
            raise serializers.ValidationError("No hospital found with this email.")
        return data

class HospitalRequestLoginOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            hospital = Hospital.objects.get(email=value)
            if not hospital.is_active:
                raise serializers.ValidationError("This hospital account is inactive. Please contact support.")

        except Hospital.DoesNotExist:
            raise serializers.ValidationError("No hospital is registered with this email.")

        # Generate a new OTP
        hospital.regenerate_otp()
        send_mail(
            'OTP for Login',
            f'Your OTP is {hospital.otp}',
            'praveencodeedex@gmail.com',
            [hospital.email]
        )
        return value

class HospitalLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            hospital = Hospital.objects.get(email=data['email'])

            if not hospital.is_active:
                raise serializers.ValidationError("This hospital account is inactive. Please contact support.")

            if hospital.is_otp_expired():
                hospital.regenerate_otp()
                send_mail(
                    'New OTP for Login',
                    f'Your new OTP is {hospital.otp}',
                    'praveencodeedex@gmail.com',
                    [hospital.email]
                )
                raise serializers.ValidationError("OTP expired. A new OTP has been sent to your email.")

            if hospital.otp != data['otp']:
                raise serializers.ValidationError("Invalid OTP.")
        except Hospital.DoesNotExist:
            raise serializers.ValidationError("No hospital is registered with this email.")

        return data

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'  # You can specify specific fields if needed

class DonorSearchSerializer(serializers.Serializer):
    blood_group = serializers.CharField(max_length=3, required=False)  # Example: 'A+', 'O-', etc.
    willing_to_donate_organs = serializers.BooleanField(required=False)
    location = serializers.CharField(max_length=100, required=False)


class BloodDonationCampScheduleSerializer(serializers.ModelSerializer):
    hospital = serializers.CharField(max_length=255)  # Accept hospital name as a string

    class Meta:
        model = BloodDonationCampSchedule
        fields = ['id', 'hospital', 'date', 'location', 'start_time', 'end_time', 'description', 'status', 'created_at']

    def validate_status(self, value):
        valid_statuses = ['scheduled', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status. Valid options are 'scheduled', 'completed', 'cancelled'.")
        return value

    def validate_date(self, value):
        """
        Ensure that the blood donation camp is not scheduled in the past.
        """
        today = timezone.now().date()
        if value < today:
            raise serializers.ValidationError("The camp date cannot be in the past.")
        return value

    def create(self, validated_data):
        # Look up hospital by name before creating a new BloodDonationCampSchedule instance
        hospital_name = validated_data['hospital']
        try:
            hospital = Hospital.objects.get(name=hospital_name)
        except Hospital.DoesNotExist:
            raise serializers.ValidationError({"hospital": f"Hospital with the name '{hospital_name}' does not exist."})

        if not hospital.is_verified or not hospital.is_active:
            raise serializers.ValidationError({"hospital": "Hospital is not verified or active."})

        validated_data['hospital'] = hospital
        return super().create(validated_data)

    def update(self, instance, validated_data):
        hospital_name = validated_data.get('hospital', None)
        if hospital_name:
            try:
                hospital = Hospital.objects.get(name=hospital_name)
            except Hospital.DoesNotExist:
                raise serializers.ValidationError({"hospital": f"Hospital with the name '{hospital_name}' does not exist."})
            validated_data['hospital'] = hospital

        return super().update(instance, validated_data)


class EmergencyDonationAlertSerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()

    class Meta:
        model = EmergencyDonationAlert
        fields = [
            'id', 'hospital','hospital_name', 'blood_group', 'organ_required',
            'location', 'message', 'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']

    def get_hospital_name(self, obj):
        return obj.hospital.name

class AnalyticsSerializer(serializers.Serializer):
    total_donors = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    total_camps = serializers.IntegerField()

class DonorStatisticsSerializer(serializers.Serializer):
    blood_group = serializers.CharField()
    count = serializers.IntegerField()

class EmergencyAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyDonationAlert
        fields = "__all__"

class SystemManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["user", "is_active", "willing_to_donate_organ"]



class UserConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConsent
        fields = ['user', 'certificate', 'consent_date', 'is_consent_given']








