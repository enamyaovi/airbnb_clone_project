from rest_framework import serializers
from listings.models import Booking, Listing, CustomUser
from datetime import date
from typing import Any


class BookingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Handles serialization and validation for Booking objects.
    Includes a computed field to return the human-readable price in cedis.
    """
    total_price_display = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'url',
            'start_date',
            'end_date',
            'total_price_display',
            'status',
            'listing'
        ]
        read_only_fields = ['total_price_display']

    def get_total_price_display(self, obj: Booking) -> str:
        """
        Return the total price in GH₵ from stored pesewa value.
        """
        return f"{obj.total_price / 100:.2f}"

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validates that:
        - end_date is after start_date
        - start_date is not in the past
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if end_date <= start_date: #type:ignore
            raise serializers.ValidationError("End date must be after start date.")
        if start_date < date.today(): #type:ignore
            raise serializers.ValidationError("You cannot book for a past date.")
        return attrs


class ListingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for property listings. Host's username is included for context.
    """
    host_username = serializers.ReadOnlyField(source='host.username')

    class Meta:
        model = Listing
        fields = [
            'url',
            'host_username',
            'name',
            'description',
            'price_per_night',
        ]
        read_only_fields = ['host']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Basic user serializer with listing links included.
    """
    listings = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='listing-detail'
    )

    class Meta:
        model = CustomUser
        fields = ['url', 'user_id', 'username', 'email', 'listings']
