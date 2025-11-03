import logging

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.dashboard.models import GlobalSetting


class MaintenanceModeMiddlewareTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        cache.clear()

    def test_response_ok_when_maintenance_mode_off(self):
        setting = GlobalSetting.objects.create(name="Default Setting")
        self.assertFalse(setting.is_maintenance_mode)

        client = APIClient()
        url = reverse("common-settings-current")
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_ok_when_maintenance_mode_on(self):
        setting = GlobalSetting.objects.create(name="Default Setting", is_maintenance_mode=True)
        self.assertTrue(setting.is_maintenance_mode)

        client = APIClient()
        url = reverse("common-settings-current")
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
