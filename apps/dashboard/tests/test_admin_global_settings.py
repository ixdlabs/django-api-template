import logging

from django.test import TestCase
from django.urls import reverse

from apps.dashboard.models import get_current_global_settings
from apps.users.models import User


class GlobalSettingsAdminTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.admin_user = User.objects.create_superuser(username="tadmin", email="tadmin@example.com", password="pass")
        self.client.login(username="tadmin", password="pass")

    # ------------------------------------------------------------------------------------------------------------------
    def test_global_settings_admin_page(self):
        global_setting = get_current_global_settings()
        list_url = reverse("admin:dashboard_globalsetting_changelist")
        response = self.client.get(list_url)
        self.assertContains(response, str(global_setting.pk))
        self.assertContains(response, "Default")

        detail_url = reverse("admin:dashboard_globalsetting_change", args=[global_setting.pk])
        response = self.client.get(detail_url)
        self.assertContains(response, str(global_setting.pk))
        self.assertContains(response, "Default")
