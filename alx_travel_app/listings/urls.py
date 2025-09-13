from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, BookingViewSet, ListingViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'listings', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
]