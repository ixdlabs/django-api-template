from django.core.cache import cache
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel

from apps.dashboard.choices import (
    EmailBackends,
    MealScannerBackends,
    OtpGenerationBackends,
    PaymentBackends,
    PushBackends,
    SmsBackends,
)
from apps.organizations.models import Organization
from apps.users.models import CustomerEnrollment
from apps.utils.cache import cache_global_property


@cache_global_property("current_global_settings", timeout=60)
def get_current_global_settings():
    setting, _ = GlobalSetting.objects.get_or_create(is_active=True, defaults={"name": "Default"})
    return setting


def get_organization_settings(organization):
    setting, _ = OrganizationSetting.objects.get_or_create(organization=organization)
    return setting


# Global Setting
# ----------------------------------------------------------------------------------------------------------------------


class OrganizationSetting(UUIDModel, TimeStampedModel, models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="settings")
    workout_schedule_price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="workout schedule price (LKR)", default=0
    )
    meal_plan_price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="meal plan price (LKR)", default=0
    )

    meal_plan_feature = models.BooleanField(
        verbose_name="meal plan feature",
        help_text="Enable or disable the meal plan feature",
        default=True,
    )
    workout_feature = models.BooleanField(
        verbose_name="workout feature",
        help_text="Enable or disable the workout feature",
        default=True,
    )
    coaches_feature = models.BooleanField(
        verbose_name="coaches feature",
        help_text="Enable or disable the coaches feature",
        default=True,
    )
    sms_marketing_feature = models.BooleanField(
        verbose_name="SMS marketing feature",
        help_text="Enable or disable the SMS marketing feature",
        default=False,
    )

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Settings for {self.organization.name}"


class GlobalSetting(UUIDModel, TimeStampedModel, models.Model):
    name = models.CharField(max_length=127, unique=True)
    is_active = models.BooleanField(default=True)
    is_maintenance_mode = models.BooleanField(default=False)
    maintenance_mode_message = models.CharField(max_length=127, blank=True)
    android_latest_version = models.CharField(blank=True)
    android_minimum_required_version = models.CharField(blank=True)
    android_update_url = models.URLField(blank=True)
    ios_latest_version = models.CharField(blank=True)
    ios_minimum_required_version = models.CharField(blank=True)
    ios_update_url = models.URLField(blank=True)

    otp_generation_feature = models.CharField(
        verbose_name="OTP generation feature",
        choices=OtpGenerationBackends.choices,
        default=OtpGenerationBackends.RANDOM,
        help_text="The backend to use for OTP generation",
    )
    otp_valid_duration_seconds = models.PositiveIntegerField(
        verbose_name="OTP valid duration",
        help_text="The amount of time an OTP will be valid (in seconds)",
        default=300,
    )
    otp_resend_wait_duration_seconds = models.PositiveIntegerField(
        verbose_name="OTP resend wait duration",
        help_text="The amount of time to wait before resending OTP (in seconds)",
        default=60,
    )
    otp_digit_count = models.PositiveIntegerField(
        verbose_name="OTP digit count",
        help_text="Number of digits in an otp",
        default=6,
    )
    otp_test_customer = models.ForeignKey(
        CustomerEnrollment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="OTP test customer",
        help_text="The customer for whom test-mode OTPs should always be generated",
    )

    email_feature = models.CharField(
        verbose_name="email feature",
        choices=EmailBackends.choices,
        default=EmailBackends.DEBUG,
        help_text="Enable or change the Email feature. "
        "Credentials must have been configured when the server was set-up.",
    )
    sms_feature = models.CharField(
        verbose_name="SMS feature",
        choices=SmsBackends.choices,
        default=SmsBackends.DEBUG,
        help_text="Enable or change the SMS feature. "
        "Credentials must have been configured when the server was set-up.",
    )
    push_feature = models.CharField(
        verbose_name="push feature",
        choices=PushBackends.choices,
        default=PushBackends.DEBUG,
        help_text="Enable or change the push notification feature. "
        "Credentials must have been configured when the server was set-up.",
    )
    email_support = models.EmailField(
        verbose_name="support email",
        help_text="The support email to use when sending outgoing emails",
        blank=True,
    )
    sms_cost = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="cost per SMS (LKR)", default=0)

    payment_feature = models.CharField(
        verbose_name="payment feature",
        choices=PaymentBackends.choices,
        default=PaymentBackends.DISABLED,
        help_text="Enable or change the payment feature. "
        "Credentials must have been configured when the server was set-up.",
    )
    recurring_payments = models.BooleanField(
        verbose_name="recurring payments",
        help_text="Whether to enable recurring payments (subscriptions)",
        default=True,
    )
    payment_sandbox = models.BooleanField(
        verbose_name="payment sandbox",
        help_text="Whether to enable sandbox mode for testing payment features",
        default=False,
    )
    meal_scanner_feature = models.CharField(
        verbose_name="meal scanner feature",
        choices=MealScannerBackends.choices,
        default=MealScannerBackends.DISABLED,
        help_text="Enable or change the meal scanner feature. "
        "Credentials must have been configured when the server was set-up.",
    )
    meal_scanner_daily_limit = models.PositiveIntegerField(
        verbose_name="meal scanner daily limit",
        help_text="Maximum number of meal scanner analyses allowed per user per day",
        default=5,
    )

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if self.is_active:
            GlobalSetting.objects.exclude(pk=self.pk).update(is_active=False)
        cache.delete("current_global_settings")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
