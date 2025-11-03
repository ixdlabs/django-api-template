import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.choices import UserTypes
from apps.users.models import User


class CustomersCustomerTests(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.customer = User.objects.create_user(
            username="customer",
            first_name="Jane",
            last_name="Customer",
            user_type=UserTypes.CUSTOMER,
        )

    # ------------------------------------------------------------------------------------------------------------------
    def test_retrieve_customer(self):
        client = APIClient()
        client.force_authenticate(self.customer)

        url = reverse("customer-customers-detail", args=[self.customer.id])
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Jane")

    # ------------------------------------------------------------------------------------------------------------------
    def test_update_customer(self):
        client = APIClient()
        client.force_authenticate(self.customer)

        url = reverse("customer-customers-detail", args=[self.customer.id])
        payload = {"first_name": "John"}
        response = client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, "John")

    # ------------------------------------------------------------------------------------------------------------------
    def test_partial_update_customer(self):
        client = APIClient()
        client.force_authenticate(self.customer)

        url = reverse("customer-customers-detail", args=[self.customer.id])
        payload = {"first_name": "John"}
        response = client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, "John")

    # ------------------------------------------------------------------------------------------------------------------
    def test_retrieve_other_customer_fails(self):
        other_customer = User.objects.create_user(
            username="customer2",
            first_name="John",
            last_name="Customer",
            user_type=UserTypes.CUSTOMER,
        )
        client = APIClient()
        client.force_authenticate(self.customer)

        url = reverse("customer-customers-detail", args=[other_customer.id])
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
