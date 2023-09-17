from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class ApiAuthTokenTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password")

    def test_token_verify(self):
        client = APIClient()
        response = client.post(
            "/api-auth/auth/login/",
            {"username": "testuser", "password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]

        response = client.post("/api-auth/token/verify/", {"token": access_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        client = APIClient()
        response = client.post(
            "/api-auth/auth/login/",
            {"username": "testuser", "password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        response = client.post("/api-auth/token/refresh/", {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_access_token = response.data["access"]
        self.assertNotEqual(access_token, new_access_token)
        self.assertIsNotNone(new_access_token)
        self.assertTrue(len(new_access_token) > 0)

    # TODO: test_token_verify__with_expired_token
    # TODO: test_token_verify__with_invalid_token
    # TODO: test_token_refresh__with_expired_token
    # TODO: test_token_refresh__with_invalid_token
