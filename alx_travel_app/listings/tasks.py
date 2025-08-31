from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment, Booking

@shared_task
def send_payment_confirmation_email(payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        booking = payment.booking
        user = booking.user

        subject = "Payment Confirmation"
        message = (
            f"Hello {user.username}, \n\n"
            f"Your payment of {payment.amount} for booking {booking.booking_id} "
            f"has been confirmed successfully. \n\n"
            "Thank you for using our service!"
        )
        recipient_list = [user.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} was not found."


@shared_task
def send_booking_confirmation_email(booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        user = booking.user

        subject = "Booking Confirmation"
        message = (
            f"Hello {user.username},\n\n"
            f"Your booking with ID {booking.booking_id} has been created successfully.\n"
            f"We’ll notify you once it’s confirmed.\n\n"
            "Thank you for booking with us!"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return f"Email sent to {user.email} for booking {booking.booking_id}"

    except Booking.DoesNotExist:
        return f"Booking with ID {booking_id} does not exist"

