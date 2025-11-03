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
            "50": "#f6fee7",
            "100": "#eafdca",
            "200": "#d7fb9b",
            "300": "#baf561",
            "400": "#a4eb3f",
            "500": "#7ed012",
            "600": "#61a60a",
            "700": "#497e0d",
            "800": "#3c6410",
            "900": "#345413",
            "950": "#192f04",
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
        {
            "title": "FCM Demo",
            "icon": "notifications",
            "link": reverse_lazy("notification_fcm_demo"),
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
                "title": "Notifications",
                "collapsible": True,
                "items": [
                    {
                        "title": "Notifications",
                        "icon": "notifications",
                        "link": changelist("notifications", "Notification"),
                    },
                    {
                        "title": "FCM Devices",
                        "icon": "phone_iphone",
                        "link": changelist("fcm_django", "FCMDevice"),
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
