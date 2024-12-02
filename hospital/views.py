from django.shortcuts import render
import random

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound, ValidationError
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


class DonorSearchView(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        # Deserialize the search parameters
        search_serializer = DonorSearchSerializer(data=request.query_params)

        if search_serializer.is_valid():
            # Extract validated data
            blood_group = search_serializer.validated_data.get('blood_group')
            willing_to_donate_organs = search_serializer.validated_data.get('willing_to_donate_organs')
            location = search_serializer.validated_data.get('location')

            # Start with the base queryset for UserProfile
            queryset = UserProfile.objects.all()

            # Apply filters if parameters are provided
            if blood_group:
                # Ensure valid blood group choice before applying the filter
                valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
                if blood_group not in valid_blood_groups:
                    raise ValidationError("Invalid blood group provided.")

                # Filter by exact blood group match
                queryset = queryset.filter(blood_group=blood_group)

            if willing_to_donate_organs is not None:
                # Filter by willing to donate organs
                queryset = queryset.filter(willing_to_donate_organ=willing_to_donate_organs)

            if location:
                # Ensure that the UserProfile has a related BloodDonationSchedule with the specified location
                queryset = queryset.filter(blooddonationschedule__location__icontains=location).distinct()

            # If no results are found, return a 404 response
            if not queryset.exists():
                return Response({"message": "No donors found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the filtered results
            donor_serializer = UserProfileSerializer(queryset, many=True)
            return Response(donor_serializer.data, status=status.HTTP_200_OK)

        # If the serializer is not valid, return errors
        return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)








