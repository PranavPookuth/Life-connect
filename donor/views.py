import random
from rest_framework.exceptions import ValidationError, NotFound
from .serializers import *
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.contrib.auth import login
from rest_framework import generics
from hospital.models import BloodDonationCampSchedule,EmergencyDonationAlert

# Create your views here.
class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful. OTP sent to your email.",
                "unique_id": user.unique_id
            }, status=status.HTTP_201_CREATED)
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

class UpcomingBloodDonationCampsView(generics.ListAPIView):
    queryset = BloodDonationCampSchedule.objects.filter(date__gte=timezone.now().date())  # Get upcoming camps
    serializer_class = BloodDonationCampScheduleSerializer
    permission_classes = []  # You can allow unauthenticated users to see upcoming camps
    authentication_classes = []


User = get_user_model()

class RegisterForCampView(generics.CreateAPIView):
    queryset = BloodDonationRegistration.objects.all()
    serializer_class = BloodDonationRegistrationSerializer
    permission_classes = []  # No authentication required
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        username = request.data.get('user')  # Accept username
        camp_id = request.data.get('camp')

        # Validate the camp
        try:
            camp = BloodDonationCampSchedule.objects.get(id=camp_id, status='scheduled')
        except BloodDonationCampSchedule.DoesNotExist:
            return Response({"error": "Invalid or unavailable camp."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the user
        try:
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response({"error": "Invalid username."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is already registered for the camp
        if BloodDonationRegistration.objects.filter(user=user_profile, camp=camp).exists():
            return Response({"error": "User is already registered for this camp."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the registration
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user_profile)  # Assign the user profile
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RegisterForCampDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BloodDonationRegistration.objects.all()
    serializer_class = BloodDonationRegistrationSerializer

class EmergencyDonationAlertListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = EmergencyDonationAlert.objects.filter(is_active=True)
    serializer_class = EmergencyDonationAlertSerializer


class DonationResponseCreateView(generics.CreateAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = DonationResponseSerializer

    def perform_create(self, serializer):
        user_name = self.request.data.get('user_name')  # Get the username from the request
        alert_id = self.kwargs['alert_id']  # Get the alert ID from the URL parameter

        try:
            # Fetch the user profile based on the provided username
            user_profile = UserProfile.objects.get(user__username=user_name)
        except UserProfile.DoesNotExist:
            raise ValidationError({"user_name": "User with this username does not exist."})

        try:
            # Fetch the alert based on the alert ID
            alert = EmergencyDonationAlert.objects.get(id=alert_id)
        except EmergencyDonationAlert.DoesNotExist:
            raise ValidationError({"alert": "Alert with this ID does not exist."})

        # Ensure that the user has not already responded to this alert
        if DonorResponse.objects.filter(user=user_profile, alert=alert).exists():
            raise ValidationError({"non_field_errors": "User has already responded to this alert."})

        # Create the donation response
        serializer.save(user=user_profile, alert=alert)
        return Response(serializer.data)

class DonorResponseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = DonorResponse.objects.all()
    serializer_class = DonationResponseSerializer
