import random
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.generics import RetrieveAPIView

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
            user.otp = None  # Clear OTP after successful verification
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

            # Reset OTP after successful login
            user.otp = None
            user.save()

            # Log in the user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Include the username in the response
            return Response(
                {
                    "user": user.username,
                    "message": "Login successful!"
                },
                status=status.HTTP_200_OK
            )
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
class UserProfileListView(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileCreateView(generics.CreateAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = UserProfileSerializer

    def perform_create(self, serializer):
        username = self.request.data.get('user')
        if not username:
            raise ValidationError({"user": "This field is required and cannot be empty."})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound({"error": f"User with username '{username}' does not exist."})

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
        try:
            return UserProfile.objects.get(pk=self.kwargs['pk'])
        except UserProfile.DoesNotExist:
            raise NotFound({"error": "User profile not found."})

    def perform_update(self, serializer):
        user_profile = self.get_object()
        serializer.save(user=user_profile.user)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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

class ChatMessageListView(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    """
    Retrieve chat history between a donor and a hospital.
    """
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        hospital_id = self.kwargs.get('hospital_id')
        return ChatMessage.objects.filter(hospital_id=hospital_id)

class ChatMessageCreateView(generics.CreateAPIView):
    permission_classes = []
    authentication_classes = []
    """
    Send a message to a hospital or from a hospital to a donor.
    """
    serializer_class = ChatMessageSerializer

    def perform_create(self, serializer):
        serializer.save()
class UserConsentListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    """API view to list all user consent records and create a new one."""
    queryset = UserConsent.objects.all()
    serializer_class = UserConsentSerializer

    def perform_create(self, serializer):
        """Override to save user consent during creation."""
        # Automatically associate the current user (if authentication is done)
        # serializer.save(user=self.request.user) # This can be added if the user is authenticated and the username is not provided
        serializer.save()

    def get_permissions(self):
        """Allow access without authentication."""
        return []  # No authentication is needed


class UserConsentRetrieveView(RetrieveAPIView):
    queryset = UserConsent.objects.all()
    serializer_class = UserConsentSerializer

    def get_object(self):
        username = self.kwargs.get('username')
        print(f"Fetching consent for username: {username}")  # Debugging
        try:
            user = User.objects.get(username=username)
            consent = UserConsent.objects.filter(user=user).first()
            if not consent:
                print(f"No consent record found for {username}")  # Debugging
                raise NotFound(f"No consent record found for username '{username}'.")
            return consent
        except User.DoesNotExist:
            print(f"User {username} does not exist")  # Debugging
            raise NotFound(f"User with username '{username}' does not exist.")


class UserConsentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    """API view to retrieve, update (re-upload certificate), and delete a user consent record."""
    queryset = UserConsent.objects.all()
    serializer_class = UserConsentSerializer

    def perform_update(self, serializer):
        """Override to handle the re-upload of the certificate."""
        # Handle the file replacement logic in the serializer, or you can process it here if needed.
        serializer.save()

    def get_permissions(self):
        """Allow access without authentication."""
        return []  # No authentication is needed

