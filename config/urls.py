from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular import views as spec_views
from rest_framework.routers import DefaultRouter

from config.admin import custom_admin_site

spectacular_api_view = spec_views.SpectacularAPIView.as_view()
spectacular_api_docs_view = spec_views.SpectacularRedocView.as_view(url_name="schema")

urlpatterns = [
    path("api-auth/", include("apps.api_auth.urls")),
    path("api-schema/", spectacular_api_view, name="schema"),
    path("api/docs/", spectacular_api_docs_view, name="redoc"),
]

router = DefaultRouter()
# TODO: Register API view sets here

urlpatterns += [
    # TODO: Register API views here
    path("api/v1/", include(router.urls)),
    path("api-schema/", spectacular_api_view, name="schema"),
    path("api/docs/", spectacular_api_docs_view, name="api_docs"),
]

urlpatterns += [
    # TODO: Configure admin site endpoint here
    path("custom-admin/", custom_admin_site.urls),
    path("", RedirectView.as_view(pattern_name="custom_admin:index")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.USE_DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
