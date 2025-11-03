import os

from celery import Celery, shared_task
from celery.signals import worker_process_init
from django_structlog.celery.steps import DjangoStructLogInitStep

from config.otel import setup_open_telemetry

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


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    setup_open_telemetry("django-api-template-celery-worker")


@shared_task
def sample_echo_task():
    return {"message": "Hello World"}
