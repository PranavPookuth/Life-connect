import pytz
from rest_framework import serializers
from .models import *
from django.core.mail import send_mail
import random
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

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