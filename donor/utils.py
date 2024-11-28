import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(to_email, otp):
    subject = 'Account Registration OTP'
    message = f'Your OTP for account registration is: {otp}'
    from_email = 'praveen.codeedex@gmail.com'  # Replace with your email
    recipient_list = [to_email]

    send_mail(subject, message, from_email, recipient_list)
