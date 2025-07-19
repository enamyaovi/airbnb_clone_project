from django.db import models
import uuid
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP

# Create your models here.
class CustomUser(AbstractUser):
    user_id = models.UUIDField(
        verbose_name='User ID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    def __str__(self) -> str:
        return self.username
    
    def get_absolute_url(self):
        return reverse('user-detail', args=[str(self.user_id)])

class Listing(models.Model):
    """
    A model for mimicing property listings
    """
    listing_id = models.UUIDField(
        verbose_name='Listing ID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    
    host = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='listings'
    )

    name = models.CharField(
        verbose_name='Listing Name',
        max_length=100,
        null=False,
    )

    description = models.TextField(
        verbose_name='Description of Property'
    )

    price_per_night = models.DecimalField(
        verbose_name='Price of Listing per Night',
        max_digits=5,
        decimal_places=2,
        null=False)
    
    created_at = models.DateTimeField(
        verbose_name='Date Listing was added',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name='Date Listing was updated',
        blank=True,
        editable=True,
        null=True
    )

    def __str__(self) -> str:
        return f"{self.name} for {self.price_per_night} cedis per night"

class Booking(models.Model):

    class BookingStatus(models.TextChoices):
        PENDING = "PND", _("Pending")
        CONFIRMED = "CFD", _("Confirmed")
        CANCELLED = "CNC", _("Cancelled")

    booking_id = models.UUIDField(
        verbose_name='Booking ID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    customer_id = models.ForeignKey(
        to=CustomUser,
        on_delete=models.RESTRICT,
        related_name='bookings'
    )

    listing_id = models.ForeignKey(
        to=Listing,
        on_delete=models.RESTRICT,
        related_name='list_bookings'
    )

    start_date = models.DateField(
        verbose_name='Start Date of Booking',
        editable=True
    )

    end_date = models.DateField(
        verbose_name='End Date of Booking',
        editable=True
    )

    total_price = models.IntegerField(
        verbose_name='Total Price of Entire Stay * 100',
        null=False,
    )

    status = models.CharField(
        verbose_name='Status of Booking',
        max_length=3,
        choices=BookingStatus,
        null=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def total_price_display(self):
        return f"GH₵{self.total_price / 100:.2f}"
    
    class Meta:
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        
        num_of_days = max((self.end_date - self.start_date).days, 1)
        price = self.listing_id.price_per_night

        total_price = Decimal(price * num_of_days*100)

        self.total_price = int(total_price.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        super().save(*args, **kwargs)

class Review(models.Model):

    review_id = models.UUIDField(
        verbose_name='Review ID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    customer_id = models.ForeignKey(
        to=CustomUser,
        on_delete=models.DO_NOTHING,
        related_name='reviews'
    )

    property_id = models.ForeignKey(
        to=Listing,
        on_delete=models.CASCADE,
        related_name='list_reviews'
        )
    
    rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    comment = models.TextField(
        null=True,
        editable=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
