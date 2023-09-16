from dj_rest_auth import views as auth_views
from dj_rest_auth.jwt_auth import get_refresh_view
from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path("login/", extend_schema(auth=[])(auth_views.LoginView).as_view(), name="rest_login"),
    path("logout/", auth_views.LogoutView.as_view(), name="rest_logout"),
    path("user/", auth_views.UserDetailsView.as_view(), name="rest_user_details"),
    path("password/change/", auth_views.PasswordChangeView.as_view(), name="rest_password_change"),
    path("password/reset/", auth_views.PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm/", auth_views.PasswordResetConfirmView.as_view(), name="rest_password_reset_confirm"),
    # Refresh token views
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
]
