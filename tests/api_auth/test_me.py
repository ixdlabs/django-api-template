from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class ApiAuthMeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password")

    def test_get_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get("/api-auth/me/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.user.id))
        self.assertEqual(response.data["username"], self.user.username)

    def test_put_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.put(
            "/api-auth/me/",
            {"first_name": "AAAAAA", "last_name": "AAAAAA"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.user.id))
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["first_name"], "AAAAAA")

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "AAAAAA")

    def test_patch_user(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.patch(
            "/api-auth/me/",
            {"first_name": "BBBBBB"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.user.id))
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["first_name"], "BBBBBB")

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "BBBBBB")
