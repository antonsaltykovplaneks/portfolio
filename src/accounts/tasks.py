from decouple import config
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail

from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def generate_verification_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_link = reverse("verify_email", kwargs={"uidb64": uid, "token": token})
    return f"https://{config("MALIGUN_SUBDOMAIN")}.planeks.org{verification_link}"


@shared_task
def send_email(user: str):
    verification_link = generate_verification_link(user)
    subject = "Verify Your Email Address"
    html_message = render_to_string('email_verification.html', {'user': user, 'verification_link': verification_link})
    send_mail(
        subject,
        "", 
        None,  # Uses the DEFAULT_FROM_EMAIL
        [user.email],
        html_message=html_message,
    )