from typing import Any
from django.core.management.base import BaseCommand, CommandError, CommandParser
from listings.models import Listing, Booking, Review
from django.contrib.auth import get_user_model
from faker import Faker, providers
import secrets, string, random
from datetime import date, timedelta

User = get_user_model()





class FakerProvider(providers.BaseProvider):
    def user_password(self):
        characters =    string.ascii_letters + string.digits
        password = ''.join(secrets.choice(characters) for _ in range(13))
        return password

    def booking_status_choice(self):
        choices = ["PND", "CFD", "CNC"]
        return random.choice(choices)
    
    def random_price(self):
        raw_float = random.uniform(100.00,1000.99)
        return raw_float
    
class Command(BaseCommand):
    help = 'Command for Seeding Database with Entries'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'total',
            type=int,
            default=10,
            help='A number that will be used to determine seed entries'
        )

    def handle(self, *args: Any, **options: Any) -> str | None:

        total = options['total']
        users = []
        property_listings = []

        fake = Faker()
        fake.add_provider(FakerProvider)

        for _ in range(total):
            username = fake.unique.user_name()
            password = fake.unique.user_password()
            email = fake.unique.email(safe=True, domain='gmail.com')
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                print(f"Added {username} with {email} and password: {password}")
                users.append(user) #type:ignore
            except Exception as err:
                raise err
            
        for _ in range(total*2):
            try:
                property = Listing.objects.create(
                    host = random.choice(users),
                    name = fake.catch_phrase(),
                    description = fake.text(max_nb_chars=150),
                    price_per_night = fake.random_price()
                )
                property_listings.append(property)

            except Exception as err:
                raise err
            
        for _ in range(total*2):
            try:
                fake_date = fake.date_between(date.today(), date.today()+timedelta(days=15))

                booking = Booking.objects.create(
                    customer_id = random.choice(users),
                    listing_id = random.choice(property_listings),
                    start_date = fake_date,
                    end_date = fake_date + timedelta(days=random.randint(1,5)),
                    status = fake.booking_status_choice()
                )

            except Exception as err:
                raise err

        self.stdout.write(
            self.style.SUCCESS("Data Inserted Succesfully")
        )