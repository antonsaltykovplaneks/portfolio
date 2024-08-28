from decouple import config
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import send_mail

from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from accounts.models import User


def generate_verification_link(user: User) -> str:
    """
    Generates link for email verification. For example - https://saltykov.planeks.org/verify-email/MTI/ccgxpc-a0f89a3a4da150dfd2ca4ea92ba6d4f7/

    Args:
        user (User): user object

    Returns:
        str: link for email verification
    """
    uid = urlsafe_base64_encode(force_bytes(user.id))
    token = default_token_generator.make_token(user)
    subdomain = config("MALIGUN_SUBDOMAIN")
    verification_link = reverse("verify_email", kwargs={"uidb64": uid, "token": token})
    return f"https://{subdomain}{verification_link}"


@shared_task
def send_email_celery_task(user_id: int):
    """
    Sends email with subject "Verify Your Email Address" and html message (accounts/email_verification.html) with verification link.

    Args:
        user_id (int): user id to send email
    """
    user = User.objects.get(pk=user_id)
    verification_link = generate_verification_link(user)
    subject = "Verify Your Email Address"
    html_message = render_to_string(
        "accounts/email_verification.html",
        {"user": user, "verification_link": verification_link},
    )
    send_mail(
        subject,
        "",
        None,  # Uses the DEFAULT_FROM_EMAIL
        [user.email],
        html_message=html_message,
    )
