import abc
from hashlib import sha256
from typing import Any, Optional

import requests
import structlog
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.dashboard.choices import SmsBackends
from apps.dashboard.models import get_current_global_settings
from apps.utils.exceptions import OperationException
from apps.utils.services import ServiceInfo, ServiceStatus

logger = structlog.get_logger(__name__)


# Abstract SMS Service
# ----------------------------------------------------------------------------------------------------------------------


def get_sms_service():
    global_settings = get_current_global_settings()
    if global_settings.sms_feature == SmsBackends.DEBUG:
        return _DebugSmsService()
    if global_settings.sms_feature == SmsBackends.DIALOG:
        return _DialogSmsService()
    raise OperationException(f"Unknown SMS feature value {global_settings.sms_feature}")


class SmsService(abc.ABC):
    @abc.abstractmethod
    def send_sms(self, phone_numbers: list[str], message: str, sms_mask: Optional[str] = None) -> dict[str, Any]:
        """Send an SMS to the specified phone numbers with the SMS mask if possible"""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_service_info(self) -> ServiceInfo:
        """Get some information of the current SMS service status"""
        raise NotImplementedError()


# Debug SMS Service
# ----------------------------------------------------------------------------------------------------------------------


class _DebugSmsService(SmsService):
    def send_sms(self, phone_numbers: list[str], message: str, sms_mask: Optional[str] = None):
        logger.info("SMS outbound", phone_numbers=phone_numbers, sms_mask=sms_mask, message=message)
        return {}

    def get_service_info(self):
        return ServiceInfo("Debug", ServiceStatus.WARNING, "SMS are logged, not actually sent")
