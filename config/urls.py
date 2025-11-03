from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular import views as spec_views
from rest_framework.routers import DefaultRouter

from apps.api_auth.apis.common.views import MeCommonViewSet, TokenCommonViewSet
from apps.api_auth.apis.customer.views import AuthCustomerViewSet
from apps.dashboard.apis.common.views import GlobalSettingsCommonViewSet
from apps.users.apis.customer.views import CustomerViewSet
from apps.utils.views import PrefixedDefaultRouter
from config.schema import SpectacularRapiDocView

spectacular_api_view = spec_views.SpectacularAPIView.as_view()
spectacular_api_docs_view = SpectacularRapiDocView.as_view(url_name="schema")


customer_router = PrefixedDefaultRouter("customer")
customer_router.register("auth", AuthCustomerViewSet, basename="auth")
customer_router.register("customers", CustomerViewSet, basename="customers")


common_router = DefaultRouter()
common_router.register("auth/token", TokenCommonViewSet, basename="common-auth-token")
common_router.register("auth", MeCommonViewSet, basename="common-auth")
common_router.register("settings", GlobalSettingsCommonViewSet, basename="common-settings")

urlpatterns = [
    path("api/v1/", include(customer_router.urls)),
    path("api/v1/", include(common_router.urls)),
    path("api/schema/", spectacular_api_view, name="schema"),
    path("api/docs/", spectacular_api_docs_view, name="api_docs"),
    # Admin site URLs
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="admin:index")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.USE_DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
