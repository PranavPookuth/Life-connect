from django.http import Http404
from django.shortcuts import render
import random

from django_filters.rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter

from .serializers import *
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from django.contrib.auth import login
from rest_framework import generics
from donor.models import  UserProfile, BloodDonationSchedule
from donor.serializers import UserProfileSerializer, BloodDonationScheduleSerializer
from urllib.parse import unquote
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
        blood_group = request.query_params.get('blood_group')
        willing_to_donate_organ = request.query_params.get('willing_to_donate_organ')

        queryset = UserProfile.objects.all()
        valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

        if blood_group:
            # Normalize the blood group by stripping whitespace and converting to uppercase
            blood_group = blood_group.strip().upper()

            # Debugging: Log the normalized blood group
            print(f"Normalized blood group: {blood_group}")

            # Validate against valid blood groups
            if blood_group not in valid_blood_groups:
                return Response(
                    {
                        "error": "Invalid blood group.",
                        "provided": blood_group,
                        "valid_options": valid_blood_groups,
                    },
                    status=400
                )

            # Filter the queryset with the normalized blood group
            queryset = queryset.filter(blood_group__iexact=blood_group)

        if willing_to_donate_organ is not None:
            if willing_to_donate_organ.lower() not in ['true', 'false']:
                return Response(
                    {"error": "Invalid value for willing_to_donate_organ. Must be 'true' or 'false'."},
                    status=400
                )
            queryset = queryset.filter(willing_to_donate_organ=(willing_to_donate_organ.lower() == 'true'))

        if not queryset.exists():
            return Response({"detail": "No donors found."}, status=404)

        serializer = UserProfileSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)


class BloodDonationCampScheduleListView(generics.ListCreateAPIView):
    queryset = BloodDonationCampSchedule.objects.all()
    serializer_class = BloodDonationCampScheduleSerializer
    permission_classes = []
    permission_classes=[]

    def perform_create(self, serializer):
        # No changes needed here, since the serializer will handle the lookup
        serializer.save()

    def get_queryset(self):
        # Optional: Allow filtering by hospital name (query parameter: `hospital_name`)
        hospital_name = self.request.query_params.get('hospital_name', None)
        queryset = BloodDonationCampSchedule.objects.all()

        if hospital_name:
            queryset = queryset.filter(hospital__name__icontains=hospital_name)  # Case-insensitive filter by name

        return queryset

class BloodDonationCampScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BloodDonationCampScheduleSerializer
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        # Retrieve blood donation camp based on hospital name and schedule id
        hospital_name = self.kwargs['hospital_name']
        queryset = BloodDonationCampSchedule.objects.filter(hospital__name=hospital_name)
        return queryset

    def perform_update(self, serializer):
        # You might want to handle any custom updates here
        serializer.save()











