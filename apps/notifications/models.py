from functools import cached_property

import structlog
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.db.models.manager import Manager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from fcm_django.models import FCMDevice
from model_utils.models import TimeStampedModel, UUIDModel
from phonenumber_field.validators import validate_international_phonenumber

from apps.memberships.models import MembershipPackage
from apps.notifications.choices import (
    NotificationTypes,
    SmsCampaignStates,
    SmsGroupGenders,
)
from apps.notifications.services.email_service import get_email_service
from apps.notifications.services.push_service import (
    AllUsersTopic,
    OrganizationTopic,
    get_push_service,
)
from apps.notifications.services.sms_service import get_sms_service
from apps.organizations.models import Branch, Organization
from apps.users.models import CustomerEnrollment

logger = structlog.get_logger(__name__)


class Notification(UUIDModel, TimeStampedModel, models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization",
        help_text="For system org-less notifications, this should be empty.",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    message = models.TextField()
    sms_message = models.TextField(blank=True)
    notification_type = models.CharField(
        max_length=255, choices=NotificationTypes.choices, default=NotificationTypes.CUSTOM
    )
    data = models.JSONField(default=dict, null=True, blank=True, help_text="Raw data passed to the notification")

    mode_push = models.BooleanField(default=False, verbose_name="send as a push notification")
    mode_sms = models.BooleanField(default=False, verbose_name="send as an SMS")
    mode_email = models.BooleanField(default=False, verbose_name="send as an email")

    is_broadcast = models.BooleanField(
        help_text="Whether this message sent to all users in the system. "
        "If this is checked, no need to set recipient users separately.",
        default=False,
    )
    recipient_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        verbose_name="recipients",
        help_text="All recipients of this notification. Required for push notifications.",
        blank=True,
    )
    recipient_phone_numbers = models.TextField(
        help_text="Phone numbers of all recipients separated by commas. "
        "Required for SMS mode. Will be derived from recipients if this is empty.",
        verbose_name="recipient phone numbers",
        blank=True,
    )
    recipient_emails = models.TextField(
        help_text="Email addresses of all recipients separated by commas. "
        "Required for email mode. Will be derived from recipients if this is empty.",
        verbose_name="recipient emails",
        blank=True,
    )
    recipient_push_ids = models.TextField(
        help_text="Device IDs of all recipients separated by commas. "
        "Required for push mode. Will be derived from recipients if this is empty.",
        verbose_name="recipient device IDs",
        blank=True,
    )

    reads = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="read_notifications",
        help_text="All users who have marked this notification as read.",
        blank=True,
    )

    objects: Manager["Notification"]

    def clean(self):
        if not self.mode_sms and not self.mode_push and not self.mode_email:
            raise ValidationError(_("Notification must belong to atleast one of the delivery methods (Push/SMS/EMail)"))
        if self.mode_sms and self.is_broadcast:
            raise ValidationError({"is_broadcast": _("Broadcasting is not supported with SMS services")})
        if self.mode_email and self.is_broadcast:
            raise ValidationError({"is_broadcast": _("Broadcasting is not supported with Email services")})
        for phone_number in self.recipient_phone_numbers.split(","):
            if phone_number:
                validate_international_phonenumber(phone_number)
        for email_address in self.recipient_emails.split(","):
            if email_address:
                validate_email(email_address)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def send(self):
        if self.mode_sms and not self.is_broadcast:
            self.send_sms()
            logger.info("sms notification sent (direct)", notification_id=self.id)
        if self.mode_email and not self.is_broadcast:
            self.send_email()
            logger.info("email notification sent (direct)", notification_id=self.id)
        if self.mode_push and not self.is_broadcast:
            self.send_push()
            logger.info("push notification sent (direct)", notification_id=self.id)
        if self.mode_push and self.is_broadcast:
            self.send_push_broadcast()
            logger.info("push notification sent (boradcast)", notification_id=self.id)

    def send_sms(self):
        if not self.recipient_phone_numbers:
            phone_numbers = self.recipient_users.values_list("phone_number", flat=True)
            self.recipient_phone_numbers = ",".join(map(str, filter(lambda x: x, phone_numbers)))
            self.save()
        sms_service = get_sms_service()
        sms_service.send_sms(
            phone_numbers=self.recipient_phone_numbers.split(","),
            message=self.sms_message or self.message,
            sms_mask=self.organization.sms_mask if self.organization else None,
        )

    def send_email(self):
        if not self.recipient_emails:
            emails = self.recipient_users.values_list("email", flat=True)
            self.recipient_emails = ",".join(map(str, filter(lambda x: x, emails)))
            self.save()
        email_service = get_email_service()
        email_service.send_email(emails=self.recipient_emails.split(","), subject=self.title, message=self.message)

    def send_push(self):
        if not self.recipient_push_ids:
            devices = FCMDevice.objects.filter(user__in=self.recipient_users.all())
            push_ids = devices.values_list("registration_id", flat=True)
            self.recipient_push_ids = ",".join(map(str, filter(lambda x: x, push_ids)))
            self.save()
        push_service = get_push_service()
        push_service.send_message(push_ids=self.recipient_push_ids.split(","), title=self.title, message=self.message)

    def send_push_broadcast(self):
        topic = AllUsersTopic() if self.organization is None else OrganizationTopic(self.organization)
        push_service = get_push_service()
        push_service.broadcast_message(topic=topic, title=self.title, message=self.message)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title


class SmsGroup(UUIDModel, TimeStampedModel, models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="sms_groups")
    name = models.CharField(max_length=255)
    description = models.TextField()
    gender = models.CharField(max_length=7, choices=SmsGroupGenders.choices, default=SmsGroupGenders.ANY)
    age_from = models.PositiveIntegerField(blank=True, null=True)
    age_to = models.PositiveIntegerField(blank=True, null=True)
    package = models.ForeignKey(
        MembershipPackage, on_delete=models.CASCADE, related_name="sms_groups", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "SMS group"
        verbose_name_plural = "SMS groups"
        ordering = ["-created"]

    @cached_property
    def filtered_customers(self):
        custom_customer_ids = self.sms_group_customer_assignments.values_list("customer__id", flat=True)
        filtered_customers = CustomerEnrollment.objects.exclude(id__in=custom_customer_ids).filter(branch=self.branch)

        if self.package:
            filtered_customers = filtered_customers.filter(memberships__package=self.package)

        today = self.branch.organization.date(timezone.now())
        if self.age_from:
            dob_to = today - relativedelta(years=self.age_from)
            filtered_customers = filtered_customers.filter(user__date_of_birth__lt=dob_to)
        if self.age_to:
            dob_from = today - relativedelta(years=self.age_to)
            filtered_customers = filtered_customers.filter(user__date_of_birth__gte=dob_from)

        if self.gender != SmsGroupGenders.ANY:
            filtered_customers = filtered_customers.filter(user__gender=self.gender)

        return filtered_customers.distinct()

    @cached_property
    def custom_customers(self):
        custom_customer_ids = self.sms_group_customer_assignments.values_list("customer__id", flat=True)
        custom_customers = CustomerEnrollment.objects.filter(id__in=custom_customer_ids).distinct()
        return custom_customers

    @cached_property
    def customers(self):
        return self.filtered_customers | self.custom_customers

    def clean(self):
        if self.package_id and self.branch_id and self.package and self.package.branch != self.branch:
            raise ValidationError({"package": _("Package must belong to the branch of the SMS group.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.branch} / {self.name}"


class SmsGroupCustomerAssignment(UUIDModel, TimeStampedModel, models.Model):
    group = models.ForeignKey(SmsGroup, on_delete=models.CASCADE, related_name="sms_group_customer_assignments")
    customer = models.ForeignKey(
        CustomerEnrollment, on_delete=models.CASCADE, related_name="sms_group_customer_assignments"
    )

    class Meta:
        verbose_name = "SMS group customer assignment"
        verbose_name_plural = "SMS group customer assignments"
        ordering = ["-created"]
        unique_together = ("group", "customer")

    def clean(self):
        if self.customer_id and self.group_id and self.customer.branch != self.group.branch:
            raise ValidationError({"customer": _("Customer must belong to the same branch as the SMS group.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group} / {self.customer}"


class SmsCampaign(UUIDModel, TimeStampedModel, models.Model):
    group = models.ForeignKey(SmsGroup, on_delete=models.CASCADE, related_name="sms_campaigns")
    name = models.CharField(max_length=127)
    message = models.CharField(max_length=160)
    state = models.CharField(max_length=15, choices=SmsCampaignStates.choices, default=SmsCampaignStates.PENDING)
    is_scheduled = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    scheduled_task_id = models.UUIDField(unique=True, blank=True, null=True)
    message_count = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="cost (LKR)")
    attempted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "SMS campaign"
        verbose_name_plural = "SMS campaigns"
        ordering = ["-created"]

    def clean(self):
        if self.is_scheduled and not self.scheduled_at:
            raise ValidationError({"scheduled_at": _("Scheduled time must be set if campaign is scheduled.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
