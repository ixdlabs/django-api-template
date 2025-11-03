import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.choices import UserTypes
from apps.users.models import User


class EmployeeAuthTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password",
            user_type=UserTypes.CUSTOMER,
        )

    # ------------------------------------------------------------------------------------------------------------------
    def test_login_succeeds_with_valid_username(self):
        client = APIClient()

        # Login
        url = reverse("customer-auth-login")
        response = client.post(url, {"username": "testuser", "password": "password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        access_token = response_data["access"]
        refresh_token = response_data["refresh"]
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        self.assertTrue(len(access_token) > 0)
        self.assertTrue(len(refresh_token) > 0)
        self.assertEqual(response_data["user"]["id"], str(self.user.id))

    # ------------------------------------------------------------------------------------------------------------------
    def test_login_succeeds_with_valid_email(self):
        client = APIClient()

        # Login
        url = reverse("customer-auth-login")
        response = client.post(url, {"email": "testuser@example.com", "password": "password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        access_token = response_data["access"]
        refresh_token = response_data["refresh"]
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        self.assertIsInstance(access_token, str)
        self.assertIsInstance(refresh_token, str)
        self.assertTrue(len(access_token) > 0)
        self.assertTrue(len(refresh_token) > 0)
        self.assertEqual(response_data["user"]["id"], str(self.user.id))

    # ------------------------------------------------------------------------------------------------------------------
    def test_login_fails_with_invalid_password(self):
        client = APIClient()
        url = reverse("customer-auth-login")
        response = client.post(url, {"username": "testuser", "password": "wrongpass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------
    def test_login_fails_with_nonexistent_username(self):
        client = APIClient()
        url = reverse("customer-auth-login")
        response = client.post(url, {"username": "doesnotexist", "password": "password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------
    def test_login_fails_with_nonexistent_email(self):
        client = APIClient()
        url = reverse("customer-auth-login")
        response = client.post(url, {"email": "wrong@example.com", "password": "password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------
    def test_login_fails_when_password_is_missing(self):
        client = APIClient()
        url = reverse("customer-auth-login")
        response = client.post(url, {"username": "testuser"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------
    def test_login_fails_for_non_customer_user(self):
        User.objects.create_user(username="unsetuser", password="password")

        client = APIClient()
        url = reverse("customer-auth-login")
        response = client.post(url, {"username": "unsetuser", "password": "password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
