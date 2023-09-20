import os

from celery import Celery, shared_task

# Cheat Sheet Documentation
# https://cheat.readthedocs.io/en/latest/django/celery.html

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery()

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@shared_task
def sample_echo_task():
    return {"message": "Hello World"}
