import random
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BloodDonationScheduleView(APIView):
    permission_classes = []  # No permission classes needed
    authentication_classes = []  # No authentication classes needed

    def post(self, request):
        # Extract the username from the request data
        username = request.data.get("user")
        if not username:
            return Response({"error": "User is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has donated blood within the last 90 days
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.last_donation_date and (date.today() - user_profile.last_donation_date).days < 90:
            return Response(
                {"error": "You cannot schedule a donation within 3 months of your last donation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Now we can save the blood donation schedule
        serializer = BloodDonationScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)  # Save the schedule with the user
            return Response({"message": "Blood donation scheduled successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


