import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class AuthMeTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create_user(username="testuser", password="password")

    # ------------------------------------------------------------------------------------------------------------------
    def test_me_endpoint_returns_authenticated_user_info(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        # Me
        url = reverse("common-auth-me")
        response = client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["id"], str(self.user.id))
        self.assertEqual(response_data["username"], self.user.username)
