import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from faker import Faker

from user.models import Profile  # adjust import

User = get_user_model()
fake = Faker("en_IN")


class Command(BaseCommand):
    help = "Seed fake users and profiles using Faker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of users to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        created = 0
        for _ in range(count):
            gender = random.choice(["Male", "Female"])

            first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
            last_name = fake.last_name()

            username = self._unique_username(first_name, last_name)
            email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_gender=gender,
                terms_accepted=True,
                terms_accepted_on=timezone.now(),
                is_verified=True,
                password="test@1234",  # dev only
            )

            dob = self._random_dob(21, 35)
            age = self._calculate_age(dob)

            Profile.objects.create(
                user=user,
                full_name=f"{first_name} {last_name}",
                gender=gender,
                date_of_birth=dob,
                age=age,
                city=fake.city(),
                state=fake.state(),
                country="India",
                phone1=fake.msisdn()[:10],
                height=random.choice(
                    ["5ft 2in", "5ft 4in", "5ft 6in", "5ft 8in", "5ft 10in"]
                ),
                religion=random.choice(
                    ["Hindu", "Muslim", "Christian", "Sikh"]
                ),
                caste=random.choice(
                    ["Brahmin", "Kshatriya", "Baniya", "OBC", "SC", "ST"]
                ),
                gotra=fake.last_name(),
                mother_tongue=random.choice(
                    ["Hindi", "Punjabi", "Marathi", "Gujarati", "Bengali", "Tamil"]
                ),
                education=random.choice(
                    ["B.Tech", "MBA", "M.Sc", "B.Com", "M.Tech", "PhD"]
                ),
                profession=random.choice(
                    ["Software Engineer", "Business Analyst", "Teacher", "Doctor", "Manager"]
                ),
                income=random.choice(
                    ["5 LPA", "8 LPA", "12 LPA", "18 LPA", "25 LPA"]
                ),
                occupation=random.choice(
                    ["IT", "Finance", "Healthcare", "Education", "Business"]
                ),
                looking_for="Bride" if gender == "Male" else "Groom",
                bio=fake.paragraph(nb_sentences=3),
                notes="Auto-generated test profile",
                marital_status="Single",
            )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully created {created} users & profiles")
        )

    def _unique_username(self, first, last):
        base = f"{first.lower()}.{last.lower()}"
        username = base
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        return username

    def _random_dob(self, min_age, max_age):
        today = date.today()
        start = today - timedelta(days=max_age * 365)
        end = today - timedelta(days=min_age * 365)
        return fake.date_between(start_date=start, end_date=end)

    def _calculate_age(self, dob):
        today = date.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
