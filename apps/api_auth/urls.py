from dj_rest_auth import views as auth_views
from django.urls import path

from apps.api_auth.views import (
    CustomLoginView,
    CustomPasswordChangeView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
    CustomRegisterView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    PasswordResetConfirmTemplateView,
)

urlpatterns = [
    # Auth endpoints
    path("auth/register/", CustomRegisterView.as_view(), name="rest_register"),
    path("auth/login/", CustomLoginView.as_view(), name="rest_login"),
    # Me endpoints
    path("me/", auth_views.UserDetailsView.as_view(), name="rest_me"),
    # Password endpoints
    path("password/change/", CustomPasswordChangeView.as_view(), name="rest_password_change"),
    path("password/reset/", CustomPasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm/", CustomPasswordResetConfirmView.as_view(), name="rest_password_reset_confirm"),
    path("password/reset/<uidb64>/<token>/", PasswordResetConfirmTemplateView.as_view(), name="password_reset_confirm"),
    # Token endpoints
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
