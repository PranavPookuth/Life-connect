from datetime import date

import pytz
from rest_framework import serializers
from .models import *
from django.core.mail import send_mail
import random
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from .models import User
from pytz import timezone as pytz_timezone
from django.contrib.auth import get_user_model

from hospital.models import BloodDonationCampSchedule,EmergencyDonationAlert


#user Registration using username,email,blood_type,is_organ_donor,is_blood_donor
class RegisterSerializer(serializers.ModelSerializer):
    unique_id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['unique_id', 'username', 'email', 'blood_type', 'is_blood_donor']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'blood_type': {'required': True},
            'is_blood_donor': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_blood_type(self, value):
        allowed_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if value not in allowed_blood_types:
            raise serializers.ValidationError(f"Invalid blood type. Allowed types are: {', '.join(allowed_blood_types)}")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            blood_type=validated_data['blood_type'],
            is_blood_donor=validated_data.get('is_blood_donor', False)
        )
        user.regenerate_otp()
        send_mail(
            'OTP Verification',
            f'Your OTP is {user.otp}',
            'praveencodeedex@gmail.com',
            [user.email]
        )
        return user

#Email verification using Otp
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if user.is_verified:
                raise serializers.ValidationError("This account is already verified.")
            if user.is_otp_expired():
                # Regenerate a new OTP
                user.regenerate_otp()
                send_mail(
                    'OTP Expired - New OTP',
                    f'Your new OTP is {user.otp}',
                    'praveencodeedex@gmail.com',
                    [user.email]
                )
                raise serializers.ValidationError("OTP has expired. A new OTP has been sent to your email.")
            if user.otp != data['otp']:
                raise serializers.ValidationError("Invalid OTP.")
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        return data


#requesting for otp to login
class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError("This account is not active. Please contact support.")
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email.")

        # Generate a new OTP for the user every time they request it
        otp = random.randint(100000, 999999)  # Generate a new 6-digit OTP
        user.otp = str(otp)
        user.otp_generated_at = timezone.now()  # Optionally store the timestamp of the OTP generation
        user.save()

        # Send OTP via email
        send_mail(
            'OTP Verification',
            f'Your OTP is {otp}',
            'praveencodeedex@gmail.com',
            [user.email]
        )

        return value


#login using email and otp
class VerifyOTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if user.is_otp_expired():
                user.regenerate_otp()
                send_mail(
                    'New OTP Verification',
                    f'Your new OTP is {user.otp}',
                    'praveencodeedex@gmail.com',
                    [user.email]
                )
                raise serializers.ValidationError("OTP expired. A new OTP has been sent.")
            if user.otp != data['otp']:
                raise serializers.ValidationError("Invalid OTP.")
            if not user.is_active:
                raise serializers.ValidationError("Account is inactive.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return data

#user creation
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['unique_id','id',"last_login","email","username","otp","otp_generated_at","is_verified","is_active","is_staff","is_superuser",'blood_type']

#donor profile creation
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'email', 'contact_number', 'address', 'id_proof', 'blood_group',
            'willing_to_donate_organ', 'organs_to_donate', 'willing_to_donate_blood', 'created_at'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.willing_to_donate_organ:
            representation.pop('organs_to_donate', None)
        return representation

    def validate_user(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username does not exist.")
        return value

#Scheduling Blood Donation camp
class BloodDonationScheduleSerializer(serializers.ModelSerializer):
    user = serializers.CharField(write_only=True, required=True)  # Accept username as a string

    class Meta:
        model = BloodDonationSchedule
        fields = ['id', 'user', 'date', 'location', 'is_available', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Donation date cannot be in the past.")
        return value

    def validate(self, data):
        # Perform user validation in the view, so here we just return the data
        return data

#User Updating the Availability for Blood Donation Camp
class UpdateAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['willing_to_donate_blood']

    def validate(self, data):
        profile = self.instance

        # Check if the user has donated blood before
        if not profile.last_donation_date:
            # For first-time donors, there's no need to check for next available date
            return data

        # For users who have donated before, check the next available date
        if profile.next_available_date <= date.today():
            return data

        raise serializers.ValidationError(
            f"You are not eligible to donate blood until {profile.next_available_date}."
        )
#User can Accessing Blood Donation Scheduled By hospital
class BloodDonationCampScheduleSerializer(serializers.ModelSerializer):
    hospital = serializers.StringRelatedField()  # Uses the __str__ method of the Hospital model

    class Meta:
        model = BloodDonationCampSchedule
        fields = ['id', 'hospital', 'date', 'location', 'start_time', 'end_time', 'description', 'status', 'created_at']

#User Registering For Blood donation Camp
class BloodDonationRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(write_only=True)  # Accept username in request
    user_name = serializers.SerializerMethodField(read_only=True)  # Return username in response

    class Meta:
        model = BloodDonationRegistration
        fields = ['id', 'user', 'user_name', 'camp', 'registration_date','created_at']

    def get_user_name(self, obj):
        return obj.user.user.username  # Return the username for the user
#User Recieving Emergency Alert from Hospital
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

#User Responding to Emergency Alert
class DonationResponseSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(write_only=True)  # Accept the user_name as input
    response_message = serializers.CharField(required=False)  # The message is optional
    is_available = serializers.BooleanField(required=True)  # Make 'is_available' required

    class Meta:
        model = DonorResponse
        fields = ['id', 'user_name', 'alert', 'response_message', 'responded_at', 'is_available']
        read_only_fields = ['id', 'responded_at']

    def validate_user_name(self, value):
        """Validate if the user exists based on the provided user_name."""
        try:
            user_profile = UserProfile.objects.get(user__username=value)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
        return value

    def create(self, validated_data):
        # Retrieve the user profile based on the provided user_name
        user_name = validated_data.pop('user_name')
        user_profile = UserProfile.objects.get(user__username=user_name)

        # Create the donation response with the correct user
        validated_data['user'] = user_profile
        return super().create(validated_data)

#Chatbox
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_type', 'sender_name', 'hospital', 'content', 'timestamp', 'is_read']
