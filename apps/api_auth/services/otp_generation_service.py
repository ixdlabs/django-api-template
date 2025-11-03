import abc
import secrets

import structlog

from apps.dashboard.choices import OtpGenerationBackends
from apps.dashboard.models import get_current_global_settings
from apps.utils.exceptions import OperationException

logger = structlog.get_logger(__name__)


def get_otp_generation_service():
    global_settings = get_current_global_settings()
    if global_settings.otp_generation_feature == OtpGenerationBackends.ALL_ZERO:
        return _AllZeroOtpGenerationService()
    elif global_settings.otp_generation_feature == OtpGenerationBackends.RANDOM:
        return _RandomOtpGenerationService()
    raise OperationException(f"Unknown OTP Generation feature value {global_settings.otp_generation_feature}")


class OtpGenerationService(abc.ABC):
    @abc.abstractmethod
    def generate_otp(self, otp_digit_count: int) -> str:
        """Generates an OTP with the specified digit count"""


# All Zero OTP Generation Service
# ----------------------------------------------------------------------------------------------------------------------


class _AllZeroOtpGenerationService(OtpGenerationService):
    def generate_otp(self, otp_digit_count: int) -> str:
        return "0" * otp_digit_count


# Random OTP Generation Service
# ----------------------------------------------------------------------------------------------------------------------


class _RandomOtpGenerationService(OtpGenerationService):
    def generate_otp(self, otp_digit_count: int) -> str:
        return str(secrets.randbelow(10**otp_digit_count)).zfill(otp_digit_count)
