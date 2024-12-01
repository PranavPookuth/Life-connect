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

from django.contrib.auth import get_user_model

#user Registration using username,email,blood_type,is_organ_donor,is_blood_donor
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'blood_type', 'is_organ_donor', 'is_blood_donor']  # No password field
        extra_kwargs = {
            'password': {'required': False},  # Make sure password is not required
        }

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        try:
            user = User.objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("User with this email is already verified.")
            self.context['existing_user'] = user
        except User.DoesNotExist:
            pass
        return value

    def validate_blood_type(self, value):
        allowed_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if not value:
            raise serializers.ValidationError("Blood type is required.")
        if value not in allowed_blood_types:
            raise serializers.ValidationError(f"Invalid blood type. Allowed types are: {', '.join(allowed_blood_types)}")
        return value

    def create(self, validated_data):
        if 'existing_user' in self.context:
            user = self.context['existing_user']
            user.regenerate_otp()
            send_mail(
                'OTP Verification',
                f'Your OTP is {user.otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )
            return user
        else:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                is_organ_donor=validated_data['is_organ_donor'],
                is_blood_donor=validated_data['is_blood_donor'],
                blood_type=validated_data['blood_type']
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
        fields =['id',"last_login","email","username","otp","otp_generated_at","is_verified","is_active","is_staff","is_superuser",'blood_type', 'is_organ_donor', 'is_blood_donor']

#donor profile creation
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')  # Reference the 'username' field of the user model
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'contact_number',
            'address',
            'id_proof',
            'willing_to_donate_organ',
            'blood_group',
            'organs_to_donate',
            'willing_to_donate_blood',
            'last_donation_date'
        ]


    def validate_user(self, value):
        """
        Validate if the provided username corresponds to an existing User.
        """
        try:
            # Look up the user by the username
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
        return user

    def create(self, validated_data):
        """
        Create a UserProfile using the validated data.
        Here we look up the user by username before saving.
        """
        user = validated_data.pop('user')  # Get the username from the validated data
        user_instance = User.objects.get(username=user)  # Look up the actual user object
        profile = UserProfile.objects.create(user=user_instance, **validated_data)
        return profile

    def to_representation(self, instance):
        """
        Modify the representation of the serialized data.
        Exclude `organs_to_donate` if `willing_to_donate_organ` is False.
        """
        representation = super().to_representation(instance)
        if not instance.willing_to_donate_organ:
            representation.pop('organs_to_donate', None)
        return representation

    def validate(self, data):
        # Ensure address and id_proof are required
        if 'address' not in data or data.get('address') in [None, '']:
            raise serializers.ValidationError({'address': "This field is required."})
        if 'id_proof' not in data or data.get('id_proof') in [None, '']:
            raise serializers.ValidationError({'id_proof': "This field is required."})

        # Validate blood_group
        if 'blood_group' in data and data['blood_group'] not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            raise serializers.ValidationError(
                {'blood_group': "Invalid blood group. Allowed values are A+, A-, B+, B-, AB+, AB-, O+, O-."}
            )

        # Validate organs_to_donate
        if data.get('willing_to_donate_organ') and not data.get('organs_to_donate'):
            raise serializers.ValidationError(
                {'organs_to_donate': "This field is required if willing to donate organs."}
            )
        if 'organs_to_donate' in data and data['organs_to_donate']:
            if not isinstance(data['organs_to_donate'], list):
                raise serializers.ValidationError(
                    {'organs_to_donate': "This field must be a list of organs (e.g., ['Kidney', 'Heart'])."}
                )
        return data

class BloodDonationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodDonationSchedule
        fields = ['date', 'time', 'location', 'is_available']

    def validate_date(self, value):
        # Ensure the donation date is not in the past
        if value < date.today():
            raise serializers.ValidationError("You cannot schedule a donation in the past.")
        return value

    def validate(self, data):
        # Check if the user has donated blood within the last 90 days
        user_profile = UserProfile.objects.get(user=self.context['request'].user)

        if user_profile.last_donation_date and (date.today() - user_profile.last_donation_date).days < 90:
            raise serializers.ValidationError(
                "You cannot schedule a donation within 3 months of your last donation."
            )
        return data


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




