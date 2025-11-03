from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class SuperUserCommandTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_creates_superadmin_when_not_exists(self):
        out = StringIO()
        call_command(
            "superuser",
            "--username=testadmin",
            "--email=test@example.com",
            "--password=securepassword123",
            stdout=out,
        )
        self.assertTrue(self.User.objects.filter(username="testadmin", is_superuser=True).exists())

    def test_skips_creation_if_superadmin_exists(self):
        self.User.objects.create_superuser(username="existing", email="ex@example.com", password="x")
        out = StringIO()
        call_command(
            "superuser",
            "--username=testadmin",
            "--email=test@example.com",
            "--password=securepassword123",
            stdout=out,
        )
        self.assertFalse(self.User.objects.filter(username="testadmin").exists())
        self.assertIn("There is already a superadmin", out.getvalue())

    def test_shows_error_if_username_exists_but_not_superadmin(self):
        self.User.objects.create_user(username="testadmin", email="t@t.com", password="p")
        out = StringIO()
        call_command(
            "superuser",
            "--username=testadmin",
            "--email=test@example.com",
            "--password=securepassword123",
            stdout=out,
        )
        self.assertEqual(self.User.objects.filter(username="testadmin").count(), 1)
        self.assertIn('Username "testadmin" already exists', out.getvalue())
