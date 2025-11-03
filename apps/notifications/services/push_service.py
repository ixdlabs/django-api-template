import abc
import json
from dataclasses import dataclass
from typing import Any

import structlog
from django.conf import settings
from fcm_django.models import FCMDevice
from firebase_admin import get_app
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FcmNotification
from firebase_admin.messaging import SendResponse

from apps.dashboard.choices import PushBackends
from apps.dashboard.models import get_current_global_settings
from apps.utils.exceptions import OperationException
from apps.utils.services import ServiceInfo, ServiceStatus

logger = structlog.get_logger(__name__)


# Abstract Topics
# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class AbstractTopic(abc.ABC):
    name: str


class AllUsersTopic(AbstractTopic):
    def __init__(self):
        self.name = "all_users"


class OrganizationTopic(AbstractTopic):
    def __init__(self, organization):
        self.name = f"organization_{organization.id}"


# Abstract SMS Service
# ----------------------------------------------------------------------------------------------------------------------


def get_push_service():
    global_settings = get_current_global_settings()
    if global_settings.push_feature == PushBackends.DEBUG:
        return _DebugPushService()
    if global_settings.push_feature == PushBackends.FIREBASE:
        return _FcmPushService()
    raise OperationException(f"Unknown push feature value {global_settings.push_feature}")


class PushService(abc.ABC):
    @abc.abstractmethod
    def send_message(self, push_ids: list[str], title: str, message: str) -> dict[str, Any]:
        """Send a push Message to the specified devices"""
        raise NotImplementedError()

    @abc.abstractmethod
    def broadcast_message(self, topic: AbstractTopic, title: str, message: str) -> dict[str, Any]:
        """Send a message to a specific topic"""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_service_info(self) -> ServiceInfo:
        """Get some information of the current push service status"""
        raise NotImplementedError()


# FCM Service
# ----------------------------------------------------------------------------------------------------------------------


class _FcmPushService(PushService):
    def send_message(self, push_ids: list[str], title: str, message: str) -> dict[str, Any]:
        if not settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            raise OperationException("There are configuration issues in Firebase. Please contact administrator.")
        devices = FCMDevice.objects.filter(registration_id__in=push_ids)
        notification = FcmNotification(title=title, body=message)
        result = devices.send_message(Message(notification=notification))
        return {
            "success_count": result.response.success_count,
            "failure_count": result.response.failure_count,
            "registration_ids_sent": result.registration_ids_sent,
            "deactivated_registration_ids": result.deactivated_registration_ids,
        }

    def broadcast_message(self, topic: AbstractTopic, title: str, message: str) -> dict[str, Any]:
        if not settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            raise OperationException("There are configuration issues in Firebase. Please contact administrator.")
        notification = FcmNotification(title=title, body=message)
        result: SendResponse = FCMDevice.send_topic_message(Message(notification=notification), topic_name=topic.name)
        return {
            "message_id": result.message_id,
            "success": result.success,
            "exception": str(result.exception),
        }

    def get_service_info(self):
        if not settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            return ServiceInfo("Firebase", ServiceStatus.UNHEALTHY, "Firebase service account json not set")
        try:
            acc_json = json.loads(get_app()._credential.service_account_json)
            firebase_project_id = acc_json["project_id"]
            return ServiceInfo("Firebase", ServiceStatus.HEALTHLY, f"Project ID '{firebase_project_id}'")
        except Exception as e:
            logger.error("could not get firebase service info", e=e)
            return ServiceInfo("Firebase", ServiceStatus.UNHEALTHY, "Could not load project ID")


# Dummy Service
# ----------------------------------------------------------------------------------------------------------------------


class _DebugPushService(PushService):
    def send_message(self, push_ids: list[str], title: str, message: str) -> dict[str, Any]:
        logger.info("push outbound", title=title, message=message, push_ids=push_ids)
        return {}

    def broadcast_message(self, topic: AbstractTopic, title: str, message: str) -> dict[str, Any]:
        logger.info("push broadcast outbound", title=title, message=message, topic=topic)
        return {}

    def get_service_info(self):
        return ServiceInfo("Debug", ServiceStatus.WARNING, "Push notifications are logged, not actually sent")
