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

    path('donation-schedules/',BloodDonationScheduleCreateView.as_view(),name="bdonation-schedules/"),
    path('donation-schedules/<int:pk>/', BloodDonationScheduleDetailView.as_view(), name='donation-schedule-detail'),

    path('hospital-register/', HospitalRegisterView.as_view(), name='hospital-register'),
    path('hospital-verify-otp/', HospitalVerifyOTPView.as_view(), name='hospital-verify-otp'),
    path('hospital-request-otp/', HospitalRequestLoginOTPView.as_view(), name='hospital-request-otp'),
    path('hospital-login/', HospitalLoginView.as_view(), name='hospital-login'),
    path('hospital-details/<int:pk>/',HospitalDetailView.as_view(),name='hospital-details'),



]
