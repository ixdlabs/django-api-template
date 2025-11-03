from django.contrib import admin, messages
from fcm_django.models import FCMDevice
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    BooleanRadioFilter,
    ChoicesDropdownFilter,
)
from unfold.decorators import action, display

from apps.notifications.models import (
    Notification,
    SmsCampaign,
    SmsGroup,
    SmsGroupCustomerAssignment,
)
from apps.notifications.tasks import send_notification_task
from apps.utils.admin import make_display

admin.site.unregister(FCMDevice)

# Notification
# ----------------------------------------------------------------------------------------------------------------------


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    search_fields = [
        "title",
        "message",
        "data",
        "recipient_phone_numbers",
        "recipient_emails",
        "recipient_push_ids",
        "recipient_users__first_name",
        "recipient_users__last_name",
    ]
    date_hierarchy = "created"

    list_filter_sheet = False
    list_filter_submit = True
    list_filter = [
        ("organization", AutocompleteSelectFilter),
        ("notification_type", ChoicesDropdownFilter),
        ("mode_push", BooleanRadioFilter),
        ("mode_sms", BooleanRadioFilter),
        ("mode_email", BooleanRadioFilter),
        ("is_broadcast", BooleanRadioFilter),
        ("recipient_users", AutocompleteSelectFilter),
    ]
    list_select_related = ["organization"]

    autocomplete_fields = ["organization"]
    filter_vertical = ["recipient_users"]
    readonly_fields = ["id", "created", "modified"]
    actions_submit_line = ["send_notification"]
    conditional_fields = {
        "recipient_users": "!is_broadcast",
        "recipient_phone_numbers": "mode_sms",
        "recipient_emails": "mode_email",
        "recipient_push_ids": "mode_push",
    }
    fieldsets = [
        (None, {"fields": ("notification_type", "title", "message")}),
        ("Recipients", {"fields": ("organization", "is_broadcast", "recipient_users"), "classes": ["tab"]}),
        ("Push", {"fields": ("mode_push", "recipient_push_ids"), "classes": ["tab"]}),
        ("SMS", {"fields": ("mode_sms", "recipient_phone_numbers"), "classes": ["tab"]}),
        ("Email", {"fields": ("mode_email", "recipient_emails"), "classes": ["tab"]}),
        ("MetaData", {"fields": ("id", ("created", "modified", "data")), "classes": ["tab"]}),
    ]

    list_display = [
        "_notification",
        "_notification_type",
        "_delivery_methods",
        "is_broadcast",
        "_organization",
        "created",
    ]
    _notification = make_display(
        description="notification",
        ordering="title",
        primary="title",
        secondary="message",
        image_text="notification_type",
        header=True,
    )
    _notification_type = make_display(
        description="notification type",
        ordering="notification_type",
        primary="notification_type",
        label=True,
    )
    _organization = make_display(
        description="organization",
        ordering="organization",
        primary="organization__name",
        secondary="=Organization",
        image="organization__logo",
        header=True,
    )

    @display(description="delivery methods", label=True)
    def _delivery_methods(self, obj):
        methods = []
        if obj.mode_push:
            methods.append("Push")
        if obj.mode_sms:
            methods.append("SMS")
        if obj.mode_email:
            methods.append("Email")
        return methods

    @action(description="Save and send notification")
    def send_notification(self, request, obj):
        send_notification_task.delay_on_commit(str(obj.id))
        messages.success(request, "Notification queued for execution successfully.")


@admin.register(FCMDevice)
class FcmDeviceAdmin(ModelAdmin):
    list_display = ["_device", "active", "date_created"]

    autocomplete_fields = ["user"]
    list_filter_sheet = False
    list_filter = ["active", "type"]
    list_select_related = ["user"]

    _device = make_display(
        description="device",
        ordering="name",
        primary="name",
        secondary="user",
        image_text="type",
        header=True,
    )


# SMS Campaign
# ----------------------------------------------------------------------------------------------------------------------


class SmsGroupCustomerAssignmentTabularInline(TabularInline):
    model = SmsGroupCustomerAssignment
    extra = 0
    tab = True
    fields = ["customer"]


class SmsGroupCampaignTabularInline(TabularInline):
    model = SmsCampaign
    extra = 0
    tab = True
    fields = ["name", "message", "is_scheduled", "scheduled_at", "state"]
    readonly_fields = ["state"]


@admin.register(SmsGroup)
class SmsGroupAdmin(ModelAdmin):
    search_fields = ["name", "description", "branch__name", "package__name"]

    list_filter_submit = True
    list_filter = [
        ("branch", AutocompleteSelectFilter),
        ("package", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
    ]
    list_per_page = 20

    inlines = [SmsGroupCustomerAssignmentTabularInline, SmsGroupCampaignTabularInline]
    autocomplete_fields = ["branch", "package"]
    readonly_fields = ["id", "created", "modified"]
    fieldsets = [
        (None, {"fields": ("branch", "name", "description", "gender", ("age_from", "age_to"), "package")}),
        ("MetaData", {"fields": ("id", ("created", "modified"), "is_active"), "classes": ["tab"]}),
    ]

    list_display = ["_sms_group", "gender", "age_from", "age_to", "_package", "is_active", "_branch", "created"]
    _sms_group = make_display(
        description="SMS group",
        ordering="name",
        primary="name",
        secondary="description",
        image_text="name",
        header=True,
    )
    _package = make_display(
        description="package",
        ordering="package",
        primary="package__name",
        secondary="package__subtitle",
        image_text="package__duration_text",
        header=True,
    )
    _branch = make_display(
        description="branch",
        ordering="branch",
        primary="branch__name",
        secondary="branch__organization",
        image="branch__organization__logo",
        header=True,
    )


@admin.register(SmsCampaign)
class SmsCampaignAdmin(ModelAdmin):
    search_fields = ["name", "message", "group__name", "group__description"]

    list_filter_submit = True
    list_filter = [
        ("group", AutocompleteSelectFilter),
        ("group__branch", AutocompleteSelectFilter),
        ("group__is_active", BooleanRadioFilter),
    ]
    list_per_page = 20

    autocomplete_fields = ["group"]
    readonly_fields = ["id", "state", "created", "modified"]
    fieldsets = [
        (None, {"fields": ("group", ("name", "message"), ("is_scheduled", "scheduled_at"), "attempted_at")}),
        ("MetaData", {"fields": ("id", ("created", "modified"), "state"), "classes": ["tab"]}),
    ]

    list_display = ["_sms_campaign", "_sms_group", "state", "scheduled_at", "message_count", "cost", "created"]
    _sms_campaign = make_display(
        description="SMS campaign",
        ordering="name",
        primary="name",
        secondary="message",
        image_text="name",
        header=True,
    )
    _sms_group = make_display(
        description="SMS group",
        ordering="group__name",
        primary="group__name",
        secondary="group__description",
        image_text="group__name",
        header=True,
    )
