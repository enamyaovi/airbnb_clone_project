from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from listings.models import Listing, Booking
from django.contrib.auth import get_user_model
from faker import Faker, providers
from datetime import date, timedelta
import secrets, string, random
from utils.logger import logger
from django.contrib.auth.models import AbstractUser
from utils.decorators import exception_handler

User = get_user_model()

class FakerProvider(providers.BaseProvider):
    """
    Custom provider for Faker that adds methods to generate
    passwords, booking statuses, and prices.
    """
    def user_password(self) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(13))

    def booking_status_choice(self) -> str:
        return random.choice(["PND", "CFD", "CNC"])

    def random_price(self) -> float:
        return random.uniform(100.00, 1000.99)

def create_fake_user(fake: Faker) -> AbstractUser:
    """
    Creates a fake user with a unique username, email, and password.
    Returns the created User instance.
    """
    username = fake.unique.user_name()
    password = fake.unique.user_password()
    email = fake.unique.email(safe=True, domain='gmail.com')
    user = User.objects.create_user(username=username, email=email, password=password)
    logger.info(f"Created user {username} with email {email}")
    return user

def create_fake_listing(fake: Faker, host: AbstractUser) -> Listing:
    """
    Creates a fake listing for the given host (user).
    Returns the created Listing instance.
    """
    return Listing.objects.create(
        host=host,
        name=fake.catch_phrase(),
        description=fake.text(max_nb_chars=150),
        price_per_night=fake.random_price()
    )

def create_fake_booking(fake: Faker, customer: AbstractUser, listing: Listing) -> Booking:
    """
    Creates a fake booking associated with the given customer and listing.
    Returns the created Booking instance.
    """
    start_date = fake.date_between(date.today(), date.today() + timedelta(days=15))
    end_date = start_date + timedelta(days=random.randint(3, 7))
    return Booking.objects.create(
        customer=customer,
        listing=listing,
        start_date=start_date,
        end_date=end_date,
        status=fake.booking_status_choice()
    )

class Command(BaseCommand):
    help = 'Command for Seeding Database with Entries'

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Adds custom command-line arguments for the management command.
        """
        parser.add_argument(
            'total',
            type=int,
            default=10,
            help='Number of users to seed (Listings and Bookings will be 2x this)'
        )

    @exception_handler
    def handle(self, *args: Any, **options: Any) -> None:
        """
        Handles the logic for seeding the database with fake users, listings, and bookings.
        """
        total = options['total']
        fake = Faker()
        fake.add_provider(FakerProvider)

        users = []
        for _ in range(total):
            user = create_fake_user(fake)
            users.append(user)

        listings = []
        for _ in range(total * 2):
            host = random.choice(users)
            listing = create_fake_listing(fake, host)
            listings.append(listing)

        bookings = []
        for _ in range(total * 2):
            customer = random.choice(users)
            listing = random.choice(listings)
            booking = create_fake_booking(fake, customer, listing)
            bookings.append(booking)

        logger.info("Database seeded successfully.")
        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))
