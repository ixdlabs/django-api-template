from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular import views as spec_views
from rest_framework.routers import DefaultRouter

from apps.dashboard.views import DashboardView
from config.admin import custom_admin_site
from config.schema import SpectacularRapiDocView

spectacular_api_view = spec_views.SpectacularAPIView.as_view()
spectacular_api_docs_view = SpectacularRapiDocView.as_view(url_name="schema")

router = DefaultRouter()
# TODO: Register API view sets here

urlpatterns = [
    path("api-auth/", include("apps.api_auth.urls")),
    path("api/v1/", include(router.urls)),
    # TODO: Register API views here
    # Admin site URLs
    path("custom-admin/dashboard", DashboardView.as_view(), name="dashboard"),
    path("custom-admin/", custom_admin_site.urls),
    path("", RedirectView.as_view(pattern_name="custom_admin:index")),
    # API documentation URLs
    path("api-schema/", spectacular_api_view, name="schema"),
    path("api/docs/", spectacular_api_docs_view, name="api_docs"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.USE_DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
