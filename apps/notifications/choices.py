from django.db import models


class NotificationTypes(models.TextChoices):
    OTP = "OTP", "OTP"
    BIRTHDAY_WISH = "BIRTHDAY_WISH", "Birthday Wish"
    WELCOME_TO_APP = "WELCOME_TO_APP", "Welcome to App"
    WELCOME_TO_BRANCH = "WELCOME_TO_BRANCH", "Welcome to Branch"
    MEMBERSHIP_RENEW_REMINDER = "MEMBERSHIP_RENEW_REMINDER", "Membership Renew Reminder"
    MEMBERSHIP_EXPIRY = "MEMBERSHIP_EXPIRY", "Membership Expiry"
    MEMBERSHIP_CREATED = "MEMBERSHIP_CREATED", "Membership Created"
    PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
    CUSTOM = "CUSTOM", "Custom"


class SmsGroupGenders(models.TextChoices):
    ANY = "ANY", "Any"
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"


class SmsGroupCustomerTypes(models.TextChoices):
    FILTERED = "FILTERED", "Filtered"
    CUSTOM = "CUSTOM", "Custom"


class SmsCampaignStates(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    FAILED = "FAILED", "Failed"
