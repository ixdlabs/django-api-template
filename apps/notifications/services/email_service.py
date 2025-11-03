import abc
from typing import Any

import structlog
from django.conf import settings
from django.core.mail import send_mail

from apps.dashboard.choices import EmailBackends
from apps.dashboard.models import get_current_global_settings
from apps.utils.exceptions import OperationException
from apps.utils.services import ServiceInfo, ServiceStatus

logger = structlog.get_logger(__name__)


# Abstract Email Service
# ----------------------------------------------------------------------------------------------------------------------


def get_email_service():
    global_settings = get_current_global_settings()
    if global_settings.email_feature == EmailBackends.DEBUG:
        return _DebugEmailService()
    if global_settings.email_feature == EmailBackends.DEFAULT:
        return _DefaultEmailService()
    raise OperationException(f"Unknown Email feature value {global_settings.email_feature}")


class EmailService(abc.ABC):
    @abc.abstractmethod
    def send_email(self, emails: list[str], subject: str, message: str) -> dict[str, Any]:
        """Sends emails to the email addresses specified"""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_service_info(self) -> ServiceInfo:
        """Get some information of the current email service status"""
        raise NotImplementedError()


# Default Email Service
# ----------------------------------------------------------------------------------------------------------------------


class _DefaultEmailService(EmailService):
    def send_email(self, emails: list[str], subject: str, message: str):
        global_settings = get_current_global_settings()
        support_email = global_settings.email_support

        msg_count = send_mail(
            subject=subject,
            message=message,
            from_email=support_email,
            recipient_list=emails,
            fail_silently=False,
        )
        logger.info("email notification sent", support_email=support_email, emails=emails, msg_count=msg_count)
        return {"msg_count": msg_count}

    def get_service_info(self):
        global_settings = get_current_global_settings()
        support_email = global_settings.email_support or settings.DEFAULT_FROM_EMAIL
        if settings.USE_RESEND:
            return ServiceInfo("Default", ServiceStatus.HEALTHLY, f"Using Resend email service (from: {support_email})")
        if settings.USE_MAILCAPTURE:
            smtp = f"{settings.EMAIL_HOST}:{settings.EMAIL_PORT}"
            return ServiceInfo("Default", ServiceStatus.HEALTHLY, f"Sending to {smtp} via SMTP (from: {support_email})")
        return ServiceInfo("Default", ServiceStatus.UNHEALTHY, "Email sender not configured")


# Debug Email Service
# ----------------------------------------------------------------------------------------------------------------------


class _DebugEmailService(EmailService):
    def send_email(self, emails: list[str], subject: str, message: str):
        logger.info("email outbound", emails=emails, subject=subject, message=message)
        return {}

    def get_service_info(self):
        return ServiceInfo("Debug", ServiceStatus.WARNING, "Emails are logged, not actually sent")
