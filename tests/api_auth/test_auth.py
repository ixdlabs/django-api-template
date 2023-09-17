from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class ApiAuthAuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password")

    def test_login__with_username(self):
        client = APIClient()
        response = client.post(
            "/api-auth/auth/login/",
            {"username": "testuser", "password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        self.assertTrue(len(access_token) > 0)
        self.assertTrue(len(refresh_token) > 0)
        self.assertEqual(response.data["user"]["id"], str(self.user.id))

    def test_login__with_email(self):
        client = APIClient()
        response = client.post(
            "/api-auth/auth/login/",
            {"email": "testuser@example.com", "password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        self.assertTrue(len(access_token) > 0)
        self.assertTrue(len(refresh_token) > 0)
        self.assertEqual(response.data["user"]["id"], str(self.user.id))

    def test_register(self):
        client = APIClient()
        response = client.post(
            "/api-auth/auth/register/",
            {
                "username": "testuser2",
                "email": "testuser2@example.com",
                "first_name": "AAAAAA",
                "last_name": "AAAAAA",
                "password1": "$tR0ngpassword",
                "password2": "$tR0ngpassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        self.assertTrue(len(access_token) > 0)
        self.assertTrue(len(refresh_token) > 0)

        user = User.objects.get(username="testuser2")
        self.assertIsNotNone(response.data["user"]["id"], str(user.id))

    # TODO: test_login__with_wrong_username
    # TODO: test_login__with_wrong_email
    # TODO: test_login__with_wrong_password
    # TODO: test_register__with_used_username
    # TODO: test_register__with_used_email
    # TODO: test_register__with_weak_password
    # TODO: test_register__with_non_matching_passwords
