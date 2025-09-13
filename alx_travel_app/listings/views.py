import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking, Payment, Listing
from .serializers import PaymentSerializer, BookingSerializer, ListingSerializer
from .tasks import send_booking_confirmation_email

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'], url_path='initiate')
    def initiate_payment(self, request):
        """
        Initiate payment with Chapa API for a given booking.
        """
        booking_id = request.data.get("booking_id")
        amount = request.data.get("amount")

        if not booking_id or not amount:
            return Response(
                {"error": "booking_id and amount are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking = Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prepare Chapa API request
        url = "https://api.chapa.co/v1/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "tx_ref": f"{booking_id}-{booking.user.id}",
            "callback_url": "https://yourdomain.com/api/payments/callback/",
            "return_url": "https://yourdomain.com/api/payment/success/",
            "customization": {
                "title": "Booking Payment",
                "description": f"Payment for booking {booking_id}",
            },
            "customer": {
                "email": booking.user.email,
                "name": booking.user.username,
            },
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            return Response(
                {"error": "Failed to connect to Chapa API.", "details": response.json()},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        chapa_response = response.json()

        if chapa_response.get("status") != "success":
            return Response(
                {"error": "Payment initiation failed.", "details": chapa_response},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract transaction ID
        transaction_id = chapa_response["data"]["tx_rf"]

        # Create payment record in db
        payment = Payment.objects.create(
            booking=booking,
            transaction_id=transaction_id,
            amount=amount,
            status=Payment.Status.PENDING,
        )

        return Response(
            {
                "message": "Payment initiated successfully.",
                "checkout_url": chapa_response["data"]["checkout_url"],
                "transaction_id": transaction_id,
                "payment_id": payment.payment_id,
                "status": payment.status,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='verify')
    def verify_payment(self, request, pk=None):
        """
        Verify a payment with Chapa and update status.
        """
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        url = f"https://api.chapa.co/v1/transaction/verify/{payment.transaction_id}"
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return Response(
                {"error": "Failed to connect to Chapa API.", "details": response.json()},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        chapa_response = response.json()

        if chapa_response.get("status") == "success":
            payment_status = Payment.Status.COMPLETED
            payment.save()
            # Trigger background email notification
            from .tasks import send_payment_confirmation_email
            send_payment_confirmation_email.delay(payment.id)
            return Response(
                {"message": "Payment verified successfully.", "status": payment.status}
            )
        else:
            payment.status = Payment.Status.FAILED
            payment.save()
            return Response(
                {"message": "Payment verification failed.", "status": payment.status},
                status=status.HTTP_400_BAD_REQUEST,
            )


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        #Trigger Celery task after booking is saved
        send_booking_confirmation_email.delay(str(booking.booking_id))


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def perform_create(self, serializer):
        listing = serializer.save()
