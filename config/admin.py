from admin_interface.admin import ThemeAdmin
from admin_interface.models import Theme
from constance.admin import Config, ConstanceAdmin
from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django_celery_beat.admin import ClockedScheduleAdmin, PeriodicTaskAdmin
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_results.admin import GroupResultAdmin, TaskResultAdmin
from django_celery_results.models import GroupResult, TaskResult


class CustomAdminSite(AdminSite):
    index_template = "admin/index.html"

    def get_app_list(self, request, *args):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """

        app_dict = self._build_app_dict(request)

        # Create a lookup map of object name to model
        app_models = {}
        for app in app_dict.values():
            for model in app["models"]:
                app_models[model["object_name"]] = model

        # Create app list as per admin_sidebar
        app_list = []
        for title, models in settings.ADMIN_MODELS:
            app = {"name": title, "models": []}
            for model in models:
                if model in app_models:
                    app["models"].append(app_models[model])
            app_list.append(app)

        return app_list


custom_admin_site = CustomAdminSite(name="custom_admin")
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Site, SiteAdmin)
custom_admin_site.register(Theme, ThemeAdmin)
custom_admin_site.register([Config], ConstanceAdmin)  # noqa

custom_admin_site.register(TaskResult, TaskResultAdmin)
custom_admin_site.register(GroupResult, GroupResultAdmin)
custom_admin_site.register(IntervalSchedule)
custom_admin_site.register(CrontabSchedule)
custom_admin_site.register(SolarSchedule)
custom_admin_site.register(ClockedSchedule, ClockedScheduleAdmin)
custom_admin_site.register(PeriodicTask, PeriodicTaskAdmin)
