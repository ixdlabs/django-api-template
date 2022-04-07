from admin_interface.admin import ThemeAdmin
from admin_interface.models import Theme
from constance.admin import Config, ConstanceAdmin
from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import TokenProxy


class CustomAdminSite(AdminSite):
    index_template = "admin/index.html"

    def get_app_list(self, request):
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


# TODO: Configure admin site name here
custom_admin_site = CustomAdminSite(name="custom_admin")
custom_admin_site.register(TokenProxy, TokenAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Site, SiteAdmin)
custom_admin_site.register(Theme, ThemeAdmin)
custom_admin_site.register([Config], ConstanceAdmin)  # noqa

# TODO: Register other third party models here
