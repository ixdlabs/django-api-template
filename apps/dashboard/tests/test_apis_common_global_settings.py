import logging

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.choices import UserTypes
from apps.users.models import User


class GlobalSettingsCommonViewSetTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create_user(username="user", user_type=UserTypes.CUSTOMER)

    def tearDown(self):
        cache.clear()

    def test_current_anonymous_user_returns_global_settings(self):
        client = APIClient()
        url = reverse("common-settings-current")
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["is_maintenance_mode"], False)

    def test_current_authenticated_user_returns_global_settings(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("common-settings-current")
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["is_maintenance_mode"], False)
