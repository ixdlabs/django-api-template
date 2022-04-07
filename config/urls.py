from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular import views as spec_views
from rest_framework.routers import DefaultRouter

from apps.users import views as user_views

spectacular_api_view = spec_views.SpectacularAPIView.as_view()
spectacular_redoc_view = spec_views.SpectacularRedocView.as_view(url_name="schema")

urlpatterns = [
    path("api-auth/", include("apps.api_auth.urls")),
    path("api-schema/", spectacular_api_view, name="schema"),
    path("api/docs/", spectacular_redoc_view, name="redoc"),
]

router = DefaultRouter()
# TODO: API view sets here

urlpatterns += [
    # TODO: API views here
    path("api/v1/", include(router.urls)),
]

urlpatterns += [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="admin:index")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
