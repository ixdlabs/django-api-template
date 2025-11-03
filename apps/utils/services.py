import dataclasses

import redis
import structlog
from django.db import models
from kombu import Connection, exceptions

from config import settings

logger = structlog.get_logger(__name__)


class ServiceStatus(models.TextChoices):
    HEALTHLY = "🟢"
    UNHEALTHY = "🔴"
    WARNING = "🟡"


@dataclasses.dataclass
class ServiceInfo:
    name: str
    status: ServiceStatus
    message: str


def get_celery_info():
    if not settings.USE_CELERY:
        return ServiceInfo("Debug", ServiceStatus.WARNING, "Tasks are running is same process, no workers")
    try:
        with Connection(settings.CELERY_BROKER_URL) as conn:
            conn.connect()
            return ServiceInfo("RabbitMQ", ServiceStatus.HEALTHLY, "Running")
    except exceptions.OperationalError as e:
        logger.error("could not connect to rabbitmq", e=e)
        return ServiceInfo("RabbitMQ", ServiceStatus.UNHEALTHY, f"Could not connect {str(e)}")
    except Exception as e:
        logger.error("unexpected error when connecting to rabbitmq", e=e)
        return ServiceInfo("RabbitMQ", ServiceStatus.UNHEALTHY, f"Unexpected error {str(e)}")


def get_cache_info():
    if not settings.REDIS_URL:
        return ServiceInfo("Debug", ServiceStatus.WARNING, "In-memory cache")
    try:
        client = redis.from_url(settings.REDIS_URL)
        if client.ping():
            return ServiceInfo("Redis", ServiceStatus.HEALTHLY, "Running")
        return ServiceInfo("Redis", ServiceStatus.UNHEALTHY, "Ping Failed")
    except redis.ConnectionError as e:
        logger.error("could not connect to redis", e=e)
        return ServiceInfo("Redis", ServiceStatus.UNHEALTHY, f"Could not connect {str(e)}")
    except Exception as e:
        logger.error("unexpected error when connecting to redis", e=e)
        return ServiceInfo("Redis", ServiceStatus.UNHEALTHY, f"Unexpected error {str(e)}")


def get_storage_info():
    if settings.USE_AZURE_BLOB:
        return ServiceInfo("Azure", ServiceStatus.HEALTHLY, "Using Azure Blob containers")
    if settings.USE_AWS_S3:
        return ServiceInfo("AWS", ServiceStatus.HEALTHLY, "Using AWS S3 Buckets")
    return ServiceInfo("Debug", ServiceStatus.WARNING, "Using server file system")
