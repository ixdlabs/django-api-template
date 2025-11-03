import logging

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from apps.users.models import User


class DemoPagesAdminTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.admin_user = User.objects.create_superuser(username="tadmin", email="tadmin@example.com", password="pass")
        self.client.login(username="tadmin", password="pass")

    def tearDown(self):
        cache.clear()

    # ------------------------------------------------------------------------------------------------------------------
    def test_schema(self):
        url = reverse("schema")
        response = self.client.get(url)
        self.assertContains(response, "schema")

    # ------------------------------------------------------------------------------------------------------------------
    def test_api_docs(self):
        url = reverse("api_docs")
        response = self.client.get(url)
        self.assertContains(response, "Backend API", status_code=200)


class BackgroundTasksAdminTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.admin_user = User.objects.create_superuser(username="tadmin", email="tadmin@example.com", password="pass")
        self.client.login(username="tadmin", password="pass")

    # ------------------------------------------------------------------------------------------------------------------
    def test_periodic_tasks_admin_page(self):
        task_1 = PeriodicTask.objects.create(
            name="testtask",
            task="config.celery.simple_echo_task",
            interval=IntervalSchedule.objects.create(every=10, period="minutes"),
        )
        task_2 = PeriodicTask.objects.create(
            name="testtask2",
            task="config.celery.simple_echo_task",
            interval=IntervalSchedule.objects.create(every=10, period="minutes"),
        )
        list_url = reverse("admin:django_celery_beat_periodictask_changelist")
        response = self.client.get(list_url)
        self.assertContains(response, str(task_1.pk))
        self.assertContains(response, str(task_2.pk))
        self.assertContains(response, "config.celery.simple_echo_task")
        detail_url = reverse("admin:django_celery_beat_periodictask_change", args=[task_1.pk])
        response = self.client.get(detail_url)
        self.assertContains(response, str(task_1.pk))
        self.assertContains(response, "config.celery.simple_echo_task")
