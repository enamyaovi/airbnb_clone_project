from listings.models import Booking, Listing, CustomUser
from rest_framework import serializers
from datetime import date


class BookingSerializer(serializers.HyperlinkedModelSerializer):
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

    def get_total_price_display(self, obj):
        return f"{obj.total_price / 100:.2f}"
    
    def validate_total_price(self, value):
        return int(float(value) * 100)
    
    def validate(self, attrs):
        start_date = attrs['start_date']
        end_date = attrs['end_date']
        if end_date <= start_date:
            raise serializers.ValidationError("End date must be after start date.")
        if start_date < date.today():
            raise serializers.ValidationError("You cannot book for a past date.")
        return attrs


class ListingSerializer(serializers.HyperlinkedModelSerializer):
    host_username = serializers.ReadOnlyField(source='host.username')
    class Meta:
        model = Listing
        fields = [
            'url',
            'host_username',
            # 'host',
            'name',
            'description',
            'price_per_night',
        ]
        read_only_fields = ['host']
    
class  UserSerializer(serializers.HyperlinkedModelSerializer):
    listings = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='listing-detail',
    )
    class Meta:
        model = CustomUser
        fields = ['url','user_id','username','email', 'listings']