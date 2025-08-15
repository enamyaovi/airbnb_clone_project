from django.db import models
import uuid, time
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP

class CustomUser(AbstractUser):
    """
    Extends Django's built-in user model to include a UUID primary key.
    """
    user_id = models.UUIDField(
        verbose_name='User ID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    def __str__(self) -> str:
        return self.username

    def get_absolute_url(self) -> str:
        return reverse('user-detail', args=[str(self.user_id)])
    
    class Meta:
        ordering = ['username']

class Listing(models.Model):
    """
    Represents a property listing posted by a host.
    """
    listing_id = models.UUIDField(
        verbose_name='Listing ID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    host = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='listings'
    )

    name = models.CharField(
        verbose_name='Listing Name',
        max_length=100,
        null=False
    )

    description = models.TextField(
        verbose_name='Description of Property'
    )

    price_per_night = models.DecimalField(
        verbose_name='Price of Listing per Night',
        max_digits=7,
        decimal_places=2,
        null=False
    )

    created_at = models.DateTimeField(
        verbose_name='Date Listing was added',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name='Date Listing was updated',
        auto_now=True
    )

    def __str__(self) -> str:
        return f"{self.name} for {self.price_per_night} cedis per night"
    
    class Meta:
        ordering = ['-created_at']

class Booking(models.Model):
    """
    Represents a booking made by a customer for a specific listing.
    Automatically calculates total cost upon save. Includes booking status choices.
    Also performs overlapping booking validation.
    """
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

    customer = models.ForeignKey(
        to=CustomUser,
        on_delete=models.RESTRICT,
        related_name='bookings'
    )

    listing = models.ForeignKey(
        to=Listing,
        on_delete=models.RESTRICT,
        related_name='bookings'
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
        verbose_name='Total Price of Entire Stay in pesewas (*100)',
        null=False
    )

    status = models.CharField(
        verbose_name='Status of Booking',
        max_length=3,
        choices=BookingStatus.choices,
        null=False,
        default=BookingStatus.PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    @property
    def total_price_display(self) -> str:
        return f"GH₵{self.total_price / 100:.2f}"

    def save(self, *args, **kwargs) -> None:
        overlapping = Booking.objects.filter(
            listing=self.listing,
            status=self.BookingStatus.CONFIRMED,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exclude(booking_id=self.booking_id).exists()

        if overlapping:
            raise ValueError("Listing already booked for selected dates")

        num_days = max((self.end_date - self.start_date).days, 1)
        price = self.listing.price_per_night
        total = Decimal(price * num_days * 100)
        self.total_price = int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        super().save(*args, **kwargs)

class Review(models.Model):
    """
    A review submitted by a customer for a specific listing.
    Includes rating and optional comment.
    """
    review_id = models.UUIDField(
        verbose_name='Review ID',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    customer = models.ForeignKey(
        to=CustomUser,
        on_delete=models.DO_NOTHING,
        related_name='reviews'
    )

    listing = models.ForeignKey(
        to=Listing,
        on_delete=models.CASCADE,
        related_name='reviews'
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

    class Meta:
        ordering = ['-created_at']

class Payment(models.Model):

    class Currency(models.TextChoices):
        # CEDIS = "GHC", _("GHANA CEDIS")
        DOLLAR = "USD", _("UNITED STATES DOLLARS")
        BIRR = "ETB", _("ETHIOPIAN BIRR")

    class PaymentStatus(models.TextChoices):
        PENDING = "PND", _("PAYMENT PENDING")
        PROCESSING = "PCS", _("PROCESSING PAYMENT")
        SUCCESS = "SCS", _("PAYMENT SUCCESSFUL")
        CANCELLED = "CND", _("PAYMENT CANCELLED")
        FAILED = "FLD", _("PAYMENT FAILED")
        REFUNDED = "RFD", _("PAYMENT REFUNDED")

    payment_id = models.UUIDField(
        default=uuid.uuid4,
        verbose_name='Payment ID',
        primary_key=True,
        editable=False
    )

    booking_reference = models.OneToOneField(
        to=Booking,
        on_delete=models.PROTECT,
        related_name='booking_payment')
    
    payment_status = models.CharField(
        max_length=3,
        choices=PaymentStatus.choices,
        null=False,
        default=PaymentStatus.PENDING)
    
    amount = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=2)
    
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        null=False,
        default=Currency.BIRR
    )
    
    transaction_id = models.CharField(
        max_length=255,
        verbose_name='ID returned by CHAPPA_PAY',
        unique=True,
        null=True,
        db_index=True)
    
    checkout_url = models.URLField(
        max_length=255,
        verbose_name='CheckOut URL from CHAPPA',
        null=True,
        blank=True)
    
    raw_request = models.JSONField(
        verbose_name= 'Outbound Payment Request Payload',
        null=True,
        blank=True)
    
    raw_response = models.JSONField(
        verbose_name='Raw Response from Chappa',
        null=True,
        blank=True)
    
    @staticmethod
    def generate_merchant_reference()->str:
        return f"{uuid.uuid4().hex[:-8]}-{int(time.time())}"

    merchant_reference = models.CharField(
        max_length= 100,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )

    webhook_event_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True)

    def __str__(self) -> str:
        return f"Booking: {self.booking_reference.pk}, Status: {self.payment_status}"
