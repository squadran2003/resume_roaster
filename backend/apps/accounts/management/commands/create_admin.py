import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from DJANGO_ADMIN_EMAIL / DJANGO_ADMIN_PASSWORD env vars if one does not already exist."

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("DJANGO_ADMIN_EMAIL", "").strip()
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "").strip()

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_ADMIN_EMAIL or DJANGO_ADMIN_PASSWORD not set — skipping admin creation."
                )
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Admin '{email}' already exists — skipping."))
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{email}' created successfully."))
