from django.db import models


class PaymentBackends(models.TextChoices):
    DISABLED = "DISABLED", "Disabled"
    PAYHERE = "PAYHERE", "Payhere"


class MealScannerBackends(models.TextChoices):
    DISABLED = "DISABLED", "Disabled"
    GEMINI = "GEMINI", "Gemini"


class EmailBackends(models.TextChoices):
    DEBUG = "DEBUG", "Debug"
    DEFAULT = "DEFAULT", "Default"


class SmsBackends(models.TextChoices):
    DEBUG = "DEBUG", "Debug"
    DIALOG = "DIALOG", "Dialog"


class PushBackends(models.TextChoices):
    DEBUG = "DEBUG", "Debug"
    FIREBASE = "FIREBASE", "Firebase"


class OtpGenerationBackends(models.TextChoices):
    ALL_ZERO = "ALL_ZERO", "All Zero"
    RANDOM = "RANDOM", "Random"


class RevenueInsightType(models.TextChoices):
    MEMBERSHIP_PACKAGE = "MEMBERSHIP_PACKAGE", "Membership Package"
    PAYMENT_METHOD = "PAYMENT_METHOD", "Payment Method"
