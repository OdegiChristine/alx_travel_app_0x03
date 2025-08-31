from rest_framework import serializers
from .models import Listing, Booking, User, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'first_name', 'last_name', 'email', 'role', 'phone_number')
        read_only_fields = ['user_id', 'role', 'email']


class ListingSerializer(serializers.ModelSerailizer):
    host = UserSerializer(read_only=True)
    host_name = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ('property_id', 'name', 'description', 'location', 'price_per_night', 'created_at', 'updated_at', 'host')
        read_only_fields = ['property_id', 'created_at', 'updated_at', 'host']

    def get_host_name(self, obj):
        return f"{obj.host.first_name} {obj.host.last_name}"


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ('booking_id', 'user', 'listing', 'created_at', 'status', 'user_name')
        read_only_fields = ['booking_id', 'user', 'listing', 'created_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
