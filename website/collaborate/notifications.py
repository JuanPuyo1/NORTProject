from django.conf import settings
from django.core.mail import send_mail


def notify_new_inquiry(inquiry):
    recipient = settings.COLLABORATION_NOTIFICATION_EMAIL
    if not recipient:
        return

    role_label = inquiry.get_role_display()
    subject = f"[NORT] Collaboration inquiry from {inquiry.name}"
    message = (
        f"New collaboration inquiry\n\n"
        f"Name: {inquiry.name}\n"
        f"Email: {inquiry.email}\n"
        f"Organization: {inquiry.organization or '—'}\n"
        f"Role: {role_label}\n\n"
        f"Message:\n{inquiry.message}\n"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )
