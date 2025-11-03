from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse_lazy


def environment_callback(request):
    if settings.DEBUG:
        return "Development", "danger"
    return "Production", "success"


def changelist(app_name: str, model_name: str):
    return reverse_lazy(f"admin:{app_name}_{model_name.lower()}_changelist")


UNFOLD_ADMIN_UI = {
    "SITE_TITLE": "Administration",
    "SITE_HEADER": "Fitconnect Admin",
    "SITE_SUBHEADER": "Fitness. Fully Connected.",
    "SITE_URL": "https://fitconnect.me",
    "BORDER_RADIUS": "12px",
    "SITE_SYMBOL": "directions_run",
    "ENVIRONMENT": "config.admin.environment_callback",
    "DASHBOARD_CALLBACK": "apps.dashboard.views.dashboard_callback",
    "LOGIN": {
        "image": lambda request: static("login.png"),
    },
    "COLORS": {
        # Generated from: https://uicolors.app/generate/a4eb3f
        "primary": {
            "50": "#eff4ff",
            "100": "#dbe5fe",
            "200": "#c0d2fd",
            "300": "#94b6fc",
            "400": "#5285f8",
            "500": "#3d68f4",
            "600": "#2749e9",
            "700": "#1f35d6",
            "800": "#1f2dae",
            "900": "#1f2b89",
            "950": "#181d53",
        },
    },
    "STYLES": [
        lambda _: static("style_fixes.css"),
    ],
    "SITE_DROPDOWN": [
        {
            "title": "Home",
            "icon": "home",
            "link": reverse_lazy("admin:index"),
        },
        {
            "title": "API Documentation",
            "icon": "api",
            "link": reverse_lazy("api_docs"),
        },
    ],
    "SIDEBAR": {
        "show_search": True,
        # Icon names are from https://fonts.google.com/icons
        "navigation": [
            {
                "title": "User Management",
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "group",
                        "link": changelist("users", "user"),
                    },
                ],
            },
            {
                "title": "Background Tasks",
                "collapsible": True,
                "items": [
                    {
                        "title": "Periodic Tasks",
                        "icon": "alarm_on",
                        "link": changelist("django_celery_beat", "PeriodicTask"),
                    },
                ],
            },
            {
                "title": "System Settings",
                "collapsible": True,
                "items": [
                    {
                        "title": "Site Configuration",
                        "icon": "globe",
                        "link": changelist("sites", "Site"),
                    },
                    {
                        "title": "Global Settings",
                        "icon": "manufacturing",
                        "link": changelist("dashboard", "GlobalSetting"),
                    },
                ],
            },
        ],
    },
}
