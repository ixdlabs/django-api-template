import structlog
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from apps.dashboard.choices import PushBackends
from apps.dashboard.models import get_current_global_settings

logger = structlog.get_logger(__name__)


class FcmNotificationsDemoView(TemplateView):
    template_name = "notifications/fcm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["firebaseVapidKeyJson"] = settings.FIREBASE_DEMO_WEB_VAPID_KEY
        context["firebaseConfigJson"] = settings.FIREBASE_DEMO_WEB_CONFIG_JSON
        return context

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        global_settings = get_current_global_settings()
        if global_settings.push_feature != PushBackends.FIREBASE:
            return HttpResponse("Current active push feature is not Firebase")
        return super().get(request, *args, **kwargs)


class FcmNotificationsDemoServiceWorkerView(TemplateView):
    template_name = "notifications/firebase-messaging-sw.js"
    content_type = "text/javascript"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = settings.FIREBASE_DEMO_WEB_CONFIG_JSON
        context["apiKey"] = config.get("apiKey")
        context["authDomain"] = config.get("authDomain")
        context["projectId"] = config.get("projectId")
        context["storageBucket"] = config.get("storageBucket")
        context["messagingSenderId"] = config.get("messagingSenderId")
        context["appId"] = config.get("appId")
        return context

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        global_settings = get_current_global_settings()
        if global_settings.push_feature != PushBackends.FIREBASE:
            return HttpResponse()
        return super().get(request, *args, **kwargs)
