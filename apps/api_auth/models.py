from datetime import datetime, timedelta
from typing import Optional

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, UUIDModel
from phonenumber_field.modelfields import PhoneNumberField

from apps.api_auth.services.otp_generation_service import (
    _AllZeroOtpGenerationService,
    get_otp_generation_service,
)
from apps.dashboard.models import get_current_global_settings
from apps.users.models import User
from apps.utils.exceptions import AuthException

# Mobile OTP
# ----------------------------------------------------------------------------------------------------------------------


class MobileOtp(UUIDModel, TimeStampedModel, models.Model):
    phone_number = PhoneNumberField()
    otp_hash = models.CharField(verbose_name="OTP Hash", max_length=1023)
    expiration_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mobile_otps", null=True, blank=True)

    @classmethod
    def generate(cls, phone_number: str, user: Optional[User] = None) -> tuple[str, datetime]:
        global_settings = get_current_global_settings()
        otp_valid_duration = global_settings.otp_valid_duration_seconds
        otp_digit_count = global_settings.otp_digit_count

        test_customer = global_settings.otp_test_customer
        if test_customer is not None and test_customer.user.phone_number == phone_number:
            otp_generation_service = _AllZeroOtpGenerationService()
        else:
            otp_generation_service = get_otp_generation_service()

        raw_otp = otp_generation_service.generate_otp(otp_digit_count)

        otp_hash = make_password(raw_otp)
        expiration_at = timezone.now() + timedelta(seconds=otp_valid_duration)

        cls.objects.update_or_create(
            user=user,
            phone_number=phone_number,
            defaults={"otp_hash": otp_hash, "expiration_at": expiration_at},
        )

        return raw_otp, expiration_at

    @classmethod
    def verify(cls, phone_number: str, otp_code: str, user: Optional[User] = None):
        try:
            obj = cls.objects.get(phone_number=phone_number, user=user)
        except cls.DoesNotExist:
            raise AuthException(_("OTP not created"))

        if obj.expiration_at < timezone.now():
            obj.delete()
            raise AuthException(_("OTP is expired"))

        if not check_password(otp_code, obj.otp_hash):
            raise AuthException(_("OTP is invalid"))

        obj.delete()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created"]
        verbose_name = "mobile OTP"
        verbose_name_plural = "mobile OTPs"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "phone_number"],
                name="unique_mobile_otp_user_phone_number",
                condition=models.Q(user__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["phone_number"],
                name="unique_mobile_otp_global_phone_number",
                condition=models.Q(user__isnull=True),
            ),
        ]

    def __str__(self):
        return f"{self.phone_number} [{self.user}]"
