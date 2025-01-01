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
    path('profiles/', UserProfileListView.as_view(), name='user-profile-list'),

    # URL to retrieve, update, or delete a UserProfile by ID
    path('user-profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),


    path('schedule-donation/', BloodDonationScheduleCreateView.as_view(), name='schedule-donation'),
    path('schedule-donation/<int:pk>/', BloodDonationScheduleDetailView.as_view(), name='schedule-donation-details'),

    path('update-availability/', UpdateAvailabilityView.as_view(), name='update-availability'),
    path('upcoming-camps/', UpcomingBloodDonationCampsView.as_view(), name='upcoming-camps'),

    path('register-camp/', RegisterForCampView.as_view(), name='register-camp'),
    path('register-camp/<int:pk>/',RegisterForCampDetailView.as_view(),name='register-camp-details'),

    path('alerts/', EmergencyDonationAlertListCreateView.as_view(), name='alert-list-create'),
    path('alerts/<int:alert_id>/respond/', DonationResponseCreateView.as_view(), name='respond-alert'),
    path('alerts/deatils/<int:pk>/',DonorResponseDetailView.as_view(),name='donor-response-details'),

    path('chat/<int:hospital_id>/', ChatMessageListView.as_view(), name='chat_history'),
    path('chat/send/', ChatMessageCreateView.as_view(), name='send_message'),
    path('messages/all/', AllChatMessagesListView.as_view(), name='all_chat_messages_list'),
    path('donor/chats/', DonorChatListView.as_view(), name='donor_chat_list'),
    path('hospital/chats/', HospitalChatListView.as_view(), name='hospital_chat_list'),

    path('consent/',UserConsentListCreateView.as_view(), name='user-consent-list-create'),
    path('consent/<int:pk>/', UserConsentRetrieveUpdateDestroyView.as_view(),
         name='user-consent-retrieve-update-destroy'),
    path('consents/<str:username>/', UserConsentRetrieveView.as_view(), name='user-consent-detail'),

]
