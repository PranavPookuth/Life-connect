from tkinter.font import names

from django.urls import path
from .views import *

urlpatterns=[

    path('hospital-register/', HospitalRegisterView.as_view(), name='hospital-register'),
    path('register-details/<int:pk>/',HospitalRegisterDetailView.as_view(),name='hospital-register-details'),
    path('hospital-verify-otp/', HospitalVerifyOTPView.as_view(), name='hospital-verify-otp'),
    path('hospital-request-otp/', HospitalRequestLoginOTPView.as_view(), name='hospital-request-otp'),
    path('hospital-login/', HospitalLoginView.as_view(), name='hospital-login'),
    path('hospital-details/<int:pk>/',HospitalDetailView.as_view(),name='hospital-details'),
    path('donors/', HospitalDonorListView.as_view(), name='hospital-donors-list'),
    path('donation-schedules/', HospitalBloodDonationScheduleListView.as_view(), name='hospital-donation-schedules'),
    path('hospital/donors/search/', DonorSearchView.as_view(), name='donor-search'),

]