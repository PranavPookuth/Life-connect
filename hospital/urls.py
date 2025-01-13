from tkinter.font import names

from django.urls import path
from .views import *

urlpatterns=[

    path('hospital-register/', HospitalRegisterView.as_view(), name='hospital-register'),
    path('register-details/<int:pk>/',HospitalRegisterDetailView.as_view(),name='hospital-register-details'),
    path('hospital-verify-otp/', HospitalVerifyOTPView.as_view(), name='hospital-verify-otp'),
    path('hospital-request-otp/', HospitalRequestLoginOTPView.as_view(), name='hospital-request-otp'),
    path('hospital-login/', HospitalLoginView.as_view(), name='hospital-login'),

    path('hospitals/',HospitalCreateView.as_view(),name='hospital'),
    path('hospital/', HospitalByNameView.as_view(), name='hospital-by-name'),

    path('hospital-details/<int:pk>/',HospitalDetailView.as_view(), name='hospital-details'),

    path('donors/', HospitalDonorListView.as_view(), name='hospital-donors-list'),
    path('hospital/donors/search/', DonorSearchView.as_view(), name='donor-search'),

    # path('hospital/certificates/', ConsentCertificateListView.as_view(), name='certificate-list-api'),

    path('hospital/blood-donation-camps/', BloodDonationCampCreateView.as_view(), name='create-camp'),
    path('hospital/blood-donation-camps-list/',BloodDonationCampListView.as_view(),name='list-camp'),
    path('hospital/blood-donation-camps/<str:hospital_name>/<int:pk>/', BloodDonationCampScheduleDetailView.as_view(),name='blood-donation-camp-detail'),

    path('camps/<int:camp_id>/donors/', DonorsForCampView.as_view(), name='donors-for-camp'),

    path('alerts/', EmergencyDonationAlertListCreateView.as_view(), name='alert-list-create'),
    path('alerts/<int:pk>/', EmergencyDonationAlertDetailView.as_view(), name='alert-detail'),

    path("dashboard/analytics/", AnalyticsView.as_view(), name="dashboard-analytics"),
    path("dashboard/donor-statistics/", DonorStatisticsView.as_view(), name="donor-statistics"),
    path("dashboard/emergency-alerts/", EmergencyAlertsListCreateView.as_view(), name="emergency-alerts-list"),
    path("dashboard/emergency-alerts/<int:pk>/", EmergencyAlertDetailView.as_view(), name="emergency-alert-detail"),
    path("dashboard/system-management/", SystemManagementView.as_view(), name="system-management"),

    path('consents/', UserConsentListView.as_view(), name='user-consent-list'),
]