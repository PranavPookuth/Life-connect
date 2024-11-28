from django.urls import path
from .views import *

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

]