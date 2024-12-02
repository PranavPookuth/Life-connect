import random

from rest_framework.exceptions import ValidationError, NotFound

from .serializers import *
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.contrib.auth import login
from rest_framework import generics

# Create your views here.
class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. OTP sent to your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            user.is_verified = True
            user.is_active = True
            user.otp = None
            user.save()
            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RequestOTPView(APIView):
    permission_classes = []
    authentication_classes = []


    def post(self, request, *args, **kwargs):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = VerifyOTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            user.otp = None
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

User = get_user_model()

class UserProfileCreateView(generics.CreateAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = UserProfileSerializer

    def perform_create(self, serializer):
        # Look up the user by username (instead of ID)
        username = self.request.data.get('user')
        user = User.objects.get(username=username)  # Lookup by username
        serializer.save(user=user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        # Retrieve the user profile using the user ID in the URL
        try:
            user_profile = UserProfile.objects.get(pk=self.kwargs['pk'])
            return user_profile
        except UserProfile.DoesNotExist:
            raise NotFound("User profile not found.")

    def perform_update(self, serializer):
        # Ensure that the profile is updated for the correct user
        user_profile = self.get_object()
        serializer.save(user=user_profile.user)  # Save the profile for the associated user

    def patch(self, request, *args, **kwargs):
        # Override the PATCH method to allow partial updates
        instance = self.get_object()  # Retrieve the profile instance

        # Update the instance with the partial data provided in the request
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Save the updated data
            return Response(serializer.data)  # Return the updated data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BloodDonationScheduleCreateView(generics.CreateAPIView):
    queryset = BloodDonationSchedule.objects.all()
    serializer_class = BloodDonationScheduleSerializer
    permission_classes = []  # No authentication needed
    authentication_classes = []

    def perform_create(self, serializer):
        # Get the username from the request data
        username = self.request.data.get('user')

        if not username:
            return Response({"detail": "User information is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up the user by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User with this username does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        donation_date = serializer.validated_data['date']

        # Check if the user has already donated within the past 3 months
        three_months_ago = timezone.now().date() - timedelta(days=90)
        last_donation = BloodDonationSchedule.objects.filter(user=user).order_by('-date').first()

        if last_donation and last_donation.date > three_months_ago:
            raise serializers.ValidationError("You have already donated blood in the last 3 months.")

        # Save the blood donation schedule if valid
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        # Override the create method to handle validation errors
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

class BloodDonationScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = BloodDonationSchedule.objects.all()
    serializer_class = BloodDonationScheduleSerializer

class UpdateAvailabilityView(APIView):
    permission_classes = []
    authentication_classes = []

    def patch(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UpdateAvailabilitySerializer(instance=profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Availability updated successfully!"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)


