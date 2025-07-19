from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.translation import gettext_lazy as _

from listings.models import Booking, Listing, Review


User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for User model.
    Includes fields, filters, and forms for user management.
    """
    change_user_password_template = None
    add_form_template = "admin/auth/user/add_form.html"

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    filter_horizontal = ("groups", "user_permissions")


class ReviewInline(admin.TabularInline):
    """
    Allows reviews to be shown inline in the listing admin view.
    """
    model = Review
    extra = 1
    readonly_fields = ("created_at",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Admin view for listings with inline reviews.
    """
    inlines = [ReviewInline]
    list_display = ("name", "host", "price_per_night", "created_at")
    list_filter = ("host",)
    search_fields = ("name", "description")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin view for bookings.
    """
    list_display = ("listing", "customer", "start_date", "end_date", "status", "total_price_display")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("listing__name", "customer__username")
    date_hierarchy = "start_date"

    @admin.display(description="Total Price (GHS)")
    def total_price_display(self, obj):
        return f"GH₵{obj.total_price / 100:.2f}"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin view for reviews.
    """
    list_display = ("listing", "customer", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("listing__name", "customer__username")
    readonly_fields = ("created_at",)
