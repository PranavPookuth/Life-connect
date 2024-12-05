from tkinter.font import names

from django.urls import path
from .views import *

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('request-otp/',RequestOTPView.as_view(),name='request-otp'),
    path('login/', LoginView.as_view(), name='login'),

    path('user/', UserListCreateView.as_view(), name='user-list'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-details'),

    path('user-profile/', UserProfileCreateView.as_view(), name='user-profile-create'),

    # URL to retrieve, update, or delete a UserProfile by ID
    path('user-profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),

    path('schedule-donation/', BloodDonationScheduleCreateView.as_view(), name='schedule-donation'),
    path('schedule-donation/<int:pk>/', BloodDonationScheduleDetailView.as_view(), name='schedule-donation-details'),
    path('update-availability/', UpdateAvailabilityView.as_view(), name='update-availability'),
    path('upcoming-camps/', UpcomingBloodDonationCampsView.as_view(), name='upcoming-camps'),
    path('register-camp/', RegisterForCampView.as_view(), name='register-camp'),
    path('register-camp/<int:pk>/',RegisterForCampDetailView.as_view(),name='register-camp-details'),
    path('alerts/', EmergencyDonationAlertListCreateView.as_view(), name='alert-list-create'),


]
