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
from django.db.models import Count
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
class HospitalCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
# Hospital Retrieve, Update, Delete View
class HospitalDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

#Donor List View
class HospitalDonorListView(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = UserProfile.objects.all()  # Fetch all donor profiles
    serializer_class = UserProfileSerializer

#Donor Search View
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

# Blood Donation camp Schedule List and create
class BloodDonationCampCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = BloodDonationCampScheduleSerializer


    def perform_create(self, serializer):
        # Retrieve hospital name from the request data (this assumes hospital name is provided)
        hospital_name = self.request.data.get('hospital', None)

        if not hospital_name:
            return Response({"detail": "Hospital name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the hospital instance by name
        try:
            hospital = Hospital.objects.get(name=hospital_name)
        except Hospital.DoesNotExist:
            return Response({"detail": f"Hospital with the name '{hospital_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the hospital is verified and active
        if not hospital.is_verified or not hospital.is_active:
            return Response({"detail": "Hospital is not verified or active."}, status=status.HTTP_403_FORBIDDEN)

        # Save the hospital instance to the camp schedule
        serializer.save(hospital=hospital)

    def create(self, request, *args, **kwargs):
        # Optionally, perform any pre-processing or additional checks here
        return super().create(request, *args, **kwargs)


# Blood Donation camp Schedule Retrieve, Update, Delete View
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

# Emergency Donation Alert List and Create
class EmergencyDonationAlertListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = EmergencyDonationAlert.objects.filter(is_active=True)
    serializer_class = EmergencyDonationAlertSerializer

    def create(self, request, *args, **kwargs):
        # Replace hospital name with its primary key in request data
        hospital_name = request.data.get('hospital')
        try:
            hospital = Hospital.objects.get(name=hospital_name)
            request.data['hospital'] = hospital.id  # Replace with PK
        except Hospital.DoesNotExist:
            raise ValidationError({'hospital': 'Hospital with this name does not exist.'})

        # Proceed with the default create logic
        return super().create(request, *args, **kwargs)


# Emergency Donation Alert Retrieve, Update, Delete View
class EmergencyDonationAlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete an EmergencyDonationAlert.
    """
    queryset = EmergencyDonationAlert.objects.all()
    serializer_class = EmergencyDonationAlertSerializer
    # Ensure these are empty only if no authentication/permissions are required
    permission_classes = []
    authentication_classes = []
#Analytics view
class AnalyticsView(APIView):
    def get(self, request):
        total_donors = UserProfile.objects.count()
        active_alerts = EmergencyDonationAlert.objects.filter(is_active=True).count()
        total_camps = BloodDonationCampSchedule.objects.count()

        data = {
            "total_donors": total_donors,
            "active_alerts": active_alerts,
            "total_camps": total_camps,
        }
        serializer = AnalyticsSerializer(data)
        return Response(serializer.data)

# Donor Statistics View
class DonorStatisticsView(APIView):
    def get(self, request):
        donors_by_blood_group = UserProfile.objects.values("blood_group").annotate(count=Count("blood_group"))
        serialized_data = [
            {"blood_group": entry["blood_group"], "count": entry["count"]}
            for entry in donors_by_blood_group
        ]
        return Response(serialized_data)

# Emergency Alerts Management Views
class EmergencyAlertsListCreateView(generics.ListCreateAPIView):
    queryset = EmergencyDonationAlert.objects.all()
    serializer_class = EmergencyAlertSerializer

class EmergencyAlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmergencyDonationAlert.objects.all()
    serializer_class = EmergencyAlertSerializer

# System Management View
class SystemManagementView(APIView):
    def get(self, request):
        users = UserProfile.objects.select_related('user').values(
            "user__username",
            "user__email",
            "user__is_active",  # Accessing the is_active field from the related User model
            "willing_to_donate_organ",
        )
        return Response(users)


