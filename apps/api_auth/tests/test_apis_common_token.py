import logging

import jwt
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.api_auth.utils import jwt_encode
from apps.users.models import User


class AuthTokenTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create_user(username="testuser", password="password")

    # ------------------------------------------------------------------------------------------------------------------
    def test_token_verify_accepts_valid_access_token(self):
        client = APIClient()
        access_token, _ = jwt_encode(self.user)

        # Token Verify
        url = reverse("common-auth-token-verify")
        response = client.post(url, {"token": str(access_token)}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------------------------------------------------------
    @override_settings(SIMPLE_JWT={"SIGNING_KEY": "secrettest"})
    def test_token_refresh_returns_new_access_token(self):
        client = APIClient()
        access_token, refresh_token = jwt_encode(self.user)

        # Token Refresh
        url = reverse("common-auth-token-refresh")
        response = client.post(url, {"refresh": str(refresh_token)}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        new_access_token = response_data["access"]
        self.assertNotEqual(access_token, new_access_token)
        self.assertIsNotNone(new_access_token)
        decoded_token = jwt.decode(new_access_token, key="secrettest", algorithms=["HS256"])
        self.assertEqual(decoded_token["user_id"], str(self.user.id))

    # ------------------------------------------------------------------------------------------------------------------
    def test_token_verify_throws_error(self):
        client = APIClient()
        url = reverse("common-auth-token-verify")
        response = client.post(url, {"token": "blahblah"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------------------------------------------------------
    @override_settings(SIMPLE_JWT={"SIGNING_KEY": "secrettest"})
    def test_token_refresh_throws_error(self):
        client = APIClient()
        url = reverse("common-auth-token-refresh")
        response = client.post(url, {"refresh": "blahblah"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
