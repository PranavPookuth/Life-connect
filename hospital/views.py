from django.shortcuts import render
import random

from django_filters.rest_framework import filters
from rest_framework.filters import SearchFilter

from .serializers import *
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.contrib.auth import login
from rest_framework import generics
from donor.models import UserProfile, BloodDonationSchedule
from donor.serializers import UserProfileSerializer, BloodDonationScheduleSerializer
# Create your views here.
class HospitalRegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = HospitalRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. OTP sent to your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HospitalRegisterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalRegisterSerializer

class HospitalVerifyOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = HospitalOTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            hospital = Hospital.objects.get(email=email)

            # Mark the hospital as verified and active
            hospital.is_verified = True
            hospital.is_active = True
            hospital.otp = None
            hospital.save()

            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HospitalRequestLoginOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = HospitalRequestLoginOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP sent successfully to your email!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HospitalLoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = HospitalLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            hospital = Hospital.objects.get(email=email)

            # Reset OTP after successful login
            hospital.otp = None
            hospital.save()

            # You can optionally create a session or token if needed
            return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HospitalDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

class HospitalDonorListView(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = UserProfile.objects.all()  # Fetch all donor profiles
    serializer_class = UserProfileSerializer

class HospitalBloodDonationScheduleListView(generics.ListAPIView):
    queryset = BloodDonationSchedule.objects.all()  # Fetch all blood donation schedules
    serializer_class = BloodDonationScheduleSerializer

class DonorSearchView(APIView):
    def get(self, request):
        # Get query parameters
        blood_group = request.query_params.get('blood_group', None)
        willing_to_donate_organ = request.query_params.get('willing_to_donate_organ', None)

        # Start with all donors
        queryset = UserProfile.objects.all()

        # Filter by blood_group if provided
        if blood_group:
            queryset = queryset.filter(blood_group__iexact=blood_group.strip())

        # Filter by willing_to_donate_organ if provided
        if willing_to_donate_organ is not None:
            queryset = queryset.filter(willing_to_donate_organ=willing_to_donate_organ.lower() == 'true')

        # Check if any donors match the filters
        if not queryset.exists():
            return Response({"detail": "No donors found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the queryset
        serializer = UserProfileSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)









