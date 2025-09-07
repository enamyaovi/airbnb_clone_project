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
        read_only_fields = ['total_price_display', 'status']

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

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering User instances   
    """

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            "password" : {
                "write_only":True
            }
        }

    def create(self, validated_data):
        """
        for creating a new user using validated data
        """
        username = validated_data.get('username', None)
        email = validated_data.get('email', None)
        password = validated_data.pop('password', None)

        if not (username and email and password):
            raise serializers.ValidationError(
                f"You are missing some values")
            #will find a way to retrieve which value(s) are empty

        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class InitiatePaymentRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.CharField()

class InitiatePaymentResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    payment_id = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)

class PaymentStatusSerializer(serializers.Serializer):
    booking_status = serializers.CharField()
    payment_status = serializers.CharField(allow_null=True)
    checkout_url = serializers.URLField(allow_null=True)


class PaymentResponseSerializer(serializers.Serializer):
    msg = serializers.CharField()
    checkout = serializers.URLField(required=False)
    redirect_url = serializers.URLField(required=False)
    status = serializers.CharField(required=False)