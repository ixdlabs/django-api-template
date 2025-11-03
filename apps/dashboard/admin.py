from django import forms
from django.contrib import admin, messages
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

from apps.dashboard.models import GlobalSetting, get_current_global_settings
from apps.utils.admin import make_display

# Celery
# ----------------------------------------------------------------------------------------------------------------------


admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    def tasks_as_choices(self):
        return tuple((a, b) for (a, b) in super().tasks_as_choices() if (not a) or a.endswith("_periodic_task"))


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    schedule_type = forms.ChoiceField(
        choices=[
            ("interval", "Interval schedule (eg. every 10 seconds)"),
            ("crontab", "Crontab schedule (eg. every day at 5:30 PM)"),
            ("solar", "Solar schedule (eg. sunrise, sunset)"),
            ("clocked", "Clocked schedule (eg. at a specific time)"),
        ],
    )
    expiration_type = forms.ChoiceField(
        choices=[
            ("none", "Does not expire"),
            ("expire_at", "Expires at a specific date and time"),
            ("expire_seconds", "Expires after a certain number of seconds"),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()
        self.fields["schedule_type"].widget = UnfoldAdminSelectWidget(choices=self.fields["schedule_type"].choices)
        self.fields["expiration_type"].widget = UnfoldAdminSelectWidget(choices=self.fields["expiration_type"].choices)

        # Set default values for schedule and timing fields based on field values
        if self.instance.interval is not None:
            self.fields["schedule_type"].initial = "interval"
        elif self.instance.crontab is not None:
            self.fields["schedule_type"].initial = "crontab"
        elif self.instance.solar is not None:
            self.fields["schedule_type"].initial = "solar"
        elif self.instance.clocked is not None:
            self.fields["schedule_type"].initial = "clocked"
        else:
            self.fields["schedule_type"].initial = "none"

        if self.instance.expires is not None:
            self.fields["expiration_type"].initial = "expire_at"
        elif self.instance.expire_seconds is not None:
            self.fields["expiration_type"].initial = "expire_seconds"
        else:
            self.fields["expiration_type"].initial = "none"

        self.fields["regtask"].initial = self.instance.task if self.instance.task else None

    def clean(self):
        data = super().clean()
        schedule_type = data.get("schedule_type")
        expiration_type = data.get("expiration_type")

        data["interval"] = None if (schedule_type != "interval") else data.get("interval")
        data["crontab"] = None if (schedule_type != "crontab") else data.get("crontab")
        data["solar"] = None if (schedule_type != "solar") else data.get("solar")
        data["clocked"] = None if (schedule_type != "clocked") else data.get("clocked")
        data["expires"] = None if (expiration_type != "expire_at") else data.get("expires")
        data["expire_seconds"] = None if (expiration_type != "expire_seconds") else data.get("expire_seconds")

        return data


@admin.register(PeriodicTask)
class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    form = UnfoldPeriodicTaskForm
    list_filter_sheet = False
    conditional_fields = {
        "interval": "schedule_type == 'interval'",
        "crontab": "schedule_type == 'crontab'",
        "crontab_translation": "schedule_type == 'crontab'",
        "solar": "schedule_type == 'solar'",
        "clocked": "schedule_type == 'clocked'",
        "expires": "expiration_type == 'expire_at'",
        "expire_seconds": "expiration_type == 'expire_seconds'",
    }
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "regtask", "task", "enabled"),
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "schedule_type",
                    "interval",
                    "crontab",
                    "crontab_translation",
                    "solar",
                    "clocked",
                    "one_off",
                ),
                "classes": ("tab",),
            },
        ),
        (
            "Timing",
            {
                "fields": ("start_time", "expiration_type", "expires", "expire_seconds", "last_run_at"),
                "classes": ("tab",),
            },
        ),
        (
            "Arguments",
            {
                "fields": ("args", "kwargs"),
                "classes": ("tab",),
            },
        ),
        (
            "Execution Options",
            {
                "fields": ("queue", "exchange", "routing_key", "priority", "headers"),
                "classes": ("tab",),
            },
        ),
    )

    list_display = ("_name", "_timing", "last_run_at", "enabled", "one_off")
    _name = make_display(
        description="periodic task",
        ordering="name",
        primary="name",
        secondary="task",
        image_text="name",
        header=True,
    )
    _timing = make_display(
        description="timing",
        ordering="start_time",
        primary="scheduler",
        secondary="=From +start_time",
        header=True,
    )


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
    pass


@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(ModelAdmin):
    pass


@admin.register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
    pass


@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(ModelAdmin):
    pass


# Site
# ----------------------------------------------------------------------------------------------------------------------


admin.site.unregister(Site)


@admin.register(Site)
class SiteAdmin(BaseSiteAdmin, ModelAdmin):
    pass


# Global Setting
# ----------------------------------------------------------------------------------------------------------------------


@admin.register(GlobalSetting)
class GlobalSettingAdmin(ModelAdmin):
    search_fields = ["name"]
    date_hierarchy = "created"

    list_filter_sheet = False
    list_filter_submit = True
    list_filter = [
        ("is_active", BooleanRadioFilter),
    ]

    actions_row = ["activate_global_setting"]
    readonly_fields = ["id", "created", "modified"]
    fieldsets = [
        (None, {"fields": ("name", "is_active")}),
        ("Maintenance", {"fields": ("is_maintenance_mode", "maintenance_mode_message"), "classes": ["tab"]}),
        ("MetaData", {"fields": ("id", ("created", "modified")), "classes": ["tab"]}),
    ]

    list_display = ["name", "is_active", "created"]

    def changelist_view(self, request, extra_context=None):
        get_current_global_settings()  # Load to initialize
        return super().changelist_view(request, extra_context)

    @action(description="Activate")
    def activate_global_setting(self, request: HttpRequest, object_id):
        setting = get_object_or_404(GlobalSetting, pk=object_id)
        setting.is_active = True
        setting.save()
        messages.success(request, f'Global setting "{setting.name}" activated successfully.')
        return redirect(reverse_lazy("admin:dashboard_globalsetting_changelist"))
