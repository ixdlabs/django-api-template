import logging

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.users.models import User


class DemoPagesAdminTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.admin_user = User.objects.create_superuser(username="tadmin", email="tadmin@example.com", password="pass")
        self.client.login(username="tadmin", password="pass")

    def tearDown(self):
        cache.clear()

    # ------------------------------------------------------------------------------------------------------------------
    def test_admin_home_page(self):
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertContains(response, "Media Storage", status_code=200)

    # ------------------------------------------------------------------------------------------------------------------
    def test_schema(self):
        url = reverse("schema")
        response = self.client.get(url)
        self.assertContains(response, "schema")

    # ------------------------------------------------------------------------------------------------------------------
    def test_api_docs(self):
        url = reverse("api_docs")
        response = self.client.get(url)
        self.assertContains(response, "Backend API", status_code=200)
