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
    permission_classes = []  # No authentication required for this view
    authentication_classes = []

    def post(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)

            # Check if this is the first-time donation (no last_donation_date)
            if not user_profile.last_donation_date:
                # First-time donation, set last_donation_date
                user_profile.last_donation_date = date.today()
                user_profile.save()
                # After saving the donation, set the next available date
                user_profile.next_available_date = user_profile.last_donation_date + timedelta(days=90)
                user_profile.save()
            elif user_profile.next_available_date > date.today():
                return Response(
                    {"error": f"You are not eligible to donate blood until {user_profile.next_available_date}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Save donation schedule and associate with the authenticated user
            serializer = BloodDonationScheduleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({"message": "Blood donation scheduled successfully!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Handle anonymous user
            # If anonymous, don't associate donation with any user
            serializer = BloodDonationScheduleSerializer(data=request.data)
            if serializer.is_valid():
                # Save donation schedule without user association for anonymous user
                serializer.save()
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


