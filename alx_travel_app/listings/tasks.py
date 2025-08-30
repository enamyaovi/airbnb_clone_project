from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_confirmation_email(to_email, booking_id, listing_title, booking_date):
    """
    Shared task to send booking confirmation email using Django's email backend.
    """
    subject = "Booking Confirmation"
    message = (
        f"Dear Customer,\n\n"
        f"Your booking has been confirmed!\n\n"
        f"Booking ID: {booking_id}\n"
        f"Listing: {listing_title}\n"
        f"Date: {booking_date}\n\n"
        f"Thank you for choosing us!"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )