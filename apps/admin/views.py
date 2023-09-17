from django.contrib import admin
from django.views.generic import TemplateView

from apps.users.models import User


class CustomDashboardView(TemplateView):
    template_name = "admin/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_apps"] = admin.site.get_app_list(self.request)
        context["number_of_users"] = User.objects.count()
        return context
