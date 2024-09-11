from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import requests

from infrastructure.models import EmailStatus


@shared_task
def send_open_notification_email(user_email, project_set_title):
    send_mail(
        subject="Your Project Set was opened",
        message=f"Someone has opened your project set: {project_set_title}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )


@shared_task
def send_shared_set_email(user_email, subject, body, project_set_id):
    response = send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )

    email_id = response.json().get("id")

    EmailStatus.objects.create(
        email_id=email_id,
        recipient_email=user_email,
        project_set_id=project_set_id,
        status="Sent",
    )


# tasks.py
@shared_task
def check_email_statuses():
    email_statuses = EmailStatus.objects.filter(status__in=["Sent", "Delivered"])
    for email_status in email_statuses:
        response = requests.get(
            f"{settings.ANYMAIL['MAILGUN_API_KEY']}/{email_status.email_id}",
            auth=("api", settings.ANYMAIL["MAILGUN_API_KEY"]),
        )

        if response.status_code == 200:
            status = response.json().get("event")
            email_status.status = status
            email_status.save()

            if status == "opened":
                send_open_notification_email.delay(
                    email_status.project_set.user.email, email_status.project_set.title
                )
        else:
            # Handle error
            pass
