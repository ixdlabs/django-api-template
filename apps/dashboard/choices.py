from django.db import models


class EmailBackends(models.TextChoices):
    DEBUG = "DEBUG", "Debug"
    DEFAULT = "DEFAULT", "Default"


class SmsBackends(models.TextChoices):
    DEBUG = "DEBUG", "Debug"


class PushBackends(models.TextChoices):
    DEBUG = "DEBUG", "Debug"
    FIREBASE = "FIREBASE", "Firebase"


class OtpGenerationBackends(models.TextChoices):
    ALL_ZERO = "ALL_ZERO", "All Zero"
    RANDOM = "RANDOM", "Random"
