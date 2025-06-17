from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django_celery_beat.admin import ClockedScheduleAdmin as BaseClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as BaseCrontabScheduleAdmin
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_results.admin import GroupResultAdmin as BaseGroupResultAdmin
from django_celery_results.admin import TaskResultAdmin as BaseTaskResultAdmin
from django_celery_results.models import GroupResult, TaskResult
from dynamic_preferences.admin import GlobalPreferenceAdmin as BaseGlobalPreferenceAdmin
from dynamic_preferences.models import GlobalPreferenceModel
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget
from unfold.decorators import display

# --------------------------------------------------------- Celery
# https://unfoldadmin.com/docs/integrations/django-celery-beat/

admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(TaskResult)
admin.site.unregister(GroupResult)


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()


@admin.register(PeriodicTask)
class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    form = UnfoldPeriodicTaskForm


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
    pass


@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(BaseCrontabScheduleAdmin, ModelAdmin):
    pass


@admin.register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
    pass


@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(BaseClockedScheduleAdmin, ModelAdmin):
    pass


@admin.register(TaskResult)
class TaskResultAdmin(BaseTaskResultAdmin, ModelAdmin):
    pass


@admin.register(GroupResult)
class GroupResultAdmin(BaseGroupResultAdmin, ModelAdmin):
    pass


# --------------------------------------------------------- Site

admin.site.unregister(Site)


@admin.register(Site)
class SiteAdmin(BaseSiteAdmin, ModelAdmin):
    pass


# --------------------------------------------------------- Preferences

admin.site.unregister(GlobalPreferenceModel)


@admin.register(GlobalPreferenceModel)
class GlobalPreferenceAdminAdmin(BaseGlobalPreferenceAdmin, ModelAdmin):
    list_display = ["_verbose_name", "_section", "_raw_value", "default_value"]

    def has_add_permission(self, request):
        return False

    @display(description=_("Value"))
    def _raw_value(self, obj):
        return obj.raw_value

    @display(description=_("Name"))
    def _verbose_name(self, obj):
        return obj.verbose_name

    @display(description=_("Section"), label=True)
    def _section(self, obj):
        return obj.section
