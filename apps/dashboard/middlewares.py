from django.http import HttpRequest, JsonResponse
from django.utils.deprecation import MiddlewareMixin

from apps.dashboard.models import get_current_global_settings


class MaintenanceModeMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        if request.path.startswith("/api/v1"):
            settings = get_current_global_settings()
            if settings.is_maintenance_mode:
                return JsonResponse(
                    {
                        "type": "service_unavailable",
                        "errors": [
                            {
                                "code": "maintenance",
                                "detail": settings.maintenance_mode_message
                                or "Service temporarily unavailable, try again later",
                            }
                        ],
                    },
                    status=503,
                )
        return None
