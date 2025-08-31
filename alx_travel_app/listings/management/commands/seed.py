from django.core.management.base import BaseCommand
from listings.models import Listing, Booking, Review
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with sample listings, bookings, and reviews"

    def handle(self, *args, **kwargs):
        host, _ = User.objects.get_or_create(
            username='samplehost',
            defaults={
                'email': 'host@example.com',
                'first_name': 'Sample',
                'last_name': 'Host',
                'role': 'host',
                'password': 'admin123'
            }
        )

        guests = []
        for i in range(5):
            guest, _ = User.objects.get_or_create(
                username=f'guest{i}',
                defaults={
                    'email': f'guest{i}@example.com',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'role': 'guest',
                    'password': 'password123'
                }
            )
            guests.append(guest)

        listings = []
        for _ in range(10):
            listing = Listing.objects.create(
                host=host,
                name=fake.company(),
                description=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                price_per_night=round(random.uniform(50.0, 500.0), 2)
            )
            listings.append(listing)

        bookings = []
        for _ in range(20):
            booking = Booking.objects.create(
                property=random.choice(listings),
                user=random.choice(guests),
                status=random.choice(['pending', 'confirmed', 'canceled'])
            )
            bookings.append(booking)

        review_count = 0
        for booking in bookings:
            if booking.status == 'confirmed':
                Review.objects.create(
                    property=booking.property,
                    user=booking.user,
                    rating=random.randint(1, 5),
                    comment=fake.sentence(),
                )
                review_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created:'))
        self.stdout.write(self.style.SUCCESS(f'  - 1 host'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(guests)} guests'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(listings)} listings'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(bookings)} bookings'))
        self.stdout.write(self.style.SUCCESS(f'  - {review_count} reviews (for confirmed bookings)'))
