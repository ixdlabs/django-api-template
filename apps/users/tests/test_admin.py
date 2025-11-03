import logging

from django.test import TestCase
from django.urls import reverse

from apps.users.choices import UserTypes
from apps.users.models import User


class OrganizationManagementAdminTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.admin_user = User.objects.create_superuser(username="tadmin", email="tadmin@example.com", password="pass")
        self.client.login(username="tadmin", password="pass")

    # ------------------------------------------------------------------------------------------------------------------
    def test_user_admin_page(self):
        u1 = User.objects.create_user(
            username="testcus1",
            user_type=UserTypes.CUSTOMER,
            first_name="testcus1first",
            last_name="testcus1last",
        )
        u2 = User.objects.create_user(
            username="testcus2",
            user_type=UserTypes.CUSTOMER,
            first_name="testcus2first",
            last_name="testcus2last",
        )
        u3 = User.objects.create_user(
            username="testunset1",
            user_type=UserTypes.UNSET,
            first_name="testunset1first",
            last_name="testunset1last",
        )
        u4 = User.objects.create_user(
            username="testunset2",
            user_type=UserTypes.UNSET,
            first_name="testunset2first",
            last_name="testunset2last",
        )

        list_url = reverse("admin:users_user_changelist")
        response = self.client.get(list_url)
        self.assertContains(response, str(self.admin_user.pk))
        self.assertContains(response, str(u1.pk))
        self.assertContains(response, str(u2.pk))
        self.assertContains(response, str(u3.pk))
        self.assertContains(response, str(u4.pk))
        self.assertContains(response, "tadmin")
        self.assertContains(response, "testcus1first testcus1last")
        self.assertContains(response, "testcus2first testcus2last")
        self.assertContains(response, "testunset1first testunset1last")
        self.assertContains(response, "testunset2first testunset2last")

    def test_user_admin_page_detail(self):
        detail_url = reverse("admin:users_user_change", args=[self.admin_user.pk])
        response = self.client.get(detail_url)
        self.assertContains(response, str(self.admin_user.pk))
        self.assertContains(response, "tadmin@example.com")
