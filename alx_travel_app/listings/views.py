from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from listings.models import Booking, Listing, Review
from listings.serializers import UserSerializer, BookingSerializer, ListingSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    Only authenticated users can access this endpoint.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    """
    Handles confirmed bookings.
    Authenticated users can create; others can read.
    """
    queryset = Booking.objects.filter(status=Booking.BookingStatus.CONFIRMED)
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically set the booking's customer to the logged-in user.
        """
        serializer.save(customer=self.request.user)

    def get_queryset(self): # type: ignore
        if self.request.user.is_authenticated:
            return Booking.objects.filter(customer=self.request.user)
        return super().get_queryset()


class ListingViewSet(viewsets.ModelViewSet):
    """
    Manages listings. Anyone can read; only authenticated users can create/edit.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
