from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_user_notification(
    context: dict, subject: str, template: str, recipients: list
):
    content = render_to_string(template, context)
    try:
        mail_sent = send_mail(
            subject=subject,
            message=content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception:
        return 1
    return mail_sent


@shared_task
def send_admin_notification(context: dict, subject: str, template: str):
    content = render_to_string(template, context)
    try:
        mail_sent = send_mail(
            subject=subject,
            message=content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL_ADDRESS],
            fail_silently=False,
        )
    except Exception:
        return 1
    return mail_sent
