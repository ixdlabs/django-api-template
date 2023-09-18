from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from apps.users.models import User


class CustomDashboardView(TemplateView):
    template_name = "admin/index.html"

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_apps"] = admin.site.get_app_list(self.request)
        context["number_of_users"] = User.objects.count()
        return context
