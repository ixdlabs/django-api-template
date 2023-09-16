import logging

from django.contrib.auth import get_user_model
from django.core.management import CommandError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates an admin user non-interactively if it doesn't exist"

    def add_arguments(self, parser):
        parser.add_argument("--username", help="Admin's username")
        parser.add_argument("--email", help="Admin's email")
        parser.add_argument("--password", help="Admin's password")

    def handle(self, *args, **options):
        user_model = get_user_model()
        if "username" in options and "email" in options and "password" in options:
            if not user_model.objects.filter(username=options["username"]).exists():
                user_model.objects.create_superuser(
                    username=options["username"], email=options["email"], password=options["password"]
                )
            else:
                logging.info(f'Username {options["username"]} already exists')
                self.stdout.write(self.style.ERROR('Username "%s" already exists' % options["username"]))
        else:
            raise CommandError("username/email/password are required fields.")
