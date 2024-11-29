import pytz
from rest_framework import serializers
from .models import *
from django.core.mail import send_mail
import random
import uuid
from django.utils import timezone

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



class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if user.is_verified:
                raise serializers.ValidationError("This account is already verified.")
            if user.otp != data['otp']:
                raise serializers.ValidationError("Invalid OTP.")
            if user.is_otp_expired():
                raise serializers.ValidationError("OTP has expired.")
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        return data


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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['id',"last_login","email","username","otp","otp_generated_at","is_verified","is_active","is_staff","is_superuser",'blood_type', 'is_organ_donor', 'is_blood_donor']


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Require a valid user ID

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'contact_number',
            'address',
            'id_proof',
            'willing_to_donate_organ',
            'blood_group'
        ]

    def validate(self, data):
        # List of required fields
        required_fields = ['user', 'contact_number', 'address', 'id_proof', 'willing_to_donate_organ', 'blood_group']

        # Check if any required field is missing or empty
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError({field: f"{field} is required."})

        # Optionally, validate specific fields further
        if data['blood_group'] not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            raise serializers.ValidationError(
                {'blood_group': "Invalid blood group. Allowed values are A+, A-, B+, B-, AB+, AB-, O+, O-."})

        return data




