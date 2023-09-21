import os
from logging.config import dictConfig

from celery import Celery, shared_task
from celery.signals import setup_logging
from django.conf import settings
from django_structlog.celery.steps import DjangoStructLogInitStep

# Cheat Sheet Documentation
# https://cheat.readthedocs.io/en/latest/django/celery.html

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery()

# A step to initialize django-structlog
app.steps["worker"].add(DjangoStructLogInitStep)
app.steps["beat"].add(DjangoStructLogInitStep)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@setup_logging.connect
def config_loggers(*args, **kwargs):
    dictConfig(settings.LOGGING)


@shared_task
def sample_echo_task():
    return {"message": "Hello World"}
