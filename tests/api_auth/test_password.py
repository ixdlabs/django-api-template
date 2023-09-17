from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class ApiAuthPasswordTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="password")

    def test_change_password(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(
            "/api-auth/password/change/",
            {"old_password": "password", "new_password1": "$tR0ngnewpassword", "new_password2": "$tR0ngnewpassword"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.logout()
        response = client.post(
            "/api-auth/auth/login/",
            {"username": "testuser", "password": "$tR0ngnewpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # TODO: test_change_password__with_invalid_old_password
    # TODO: test_change_password__with_weak_new_password
    # TODO: test_change_password__with_non_matching_new_passwords
