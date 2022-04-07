from dj_rest_auth import views as auth_views
from django.urls import path

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="rest_login"),
    path("logout/", auth_views.LogoutView.as_view(), name="rest_logout"),
    path("user/", auth_views.UserDetailsView.as_view(), name="rest_user_details"),
    path("password/change/", auth_views.PasswordChangeView.as_view(), name="rest_password_change"),
    path("password/reset/", auth_views.PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm/", auth_views.PasswordResetConfirmView.as_view(), name="rest_password_reset_confirm"),
]
