from django import template

from apps.users.models import User

register = template.Library()


@register.inclusion_tag("dashboard/dashboard.html", takes_context=True)
def dashboard(context):
    return {
        "number_of_users": User.objects.count(),
    }
