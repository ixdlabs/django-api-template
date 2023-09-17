from typing import Any

from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    sensitive_post_parameters_m,
)
from django.contrib.auth import get_user_model
from drf_spectacular.contrib.rest_auth import RestAuthDetailSerializer
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenVerifyView

from apps.api_auth.serializers import RegisterSerializer
from apps.utils.views import PublicEndpoint

user_model = get_user_model()


# ---------------------------------------- Auth


@extend_schema(responses={status.HTTP_201_CREATED: api_settings.JWT_SERIALIZER}, summary="Register a new user")
class CustomRegisterView(PublicEndpoint, CreateAPIView):
    serializer_class = RegisterSerializer

    user: Any
    access_token: str
    refresh_token: str

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = {
            "user": self.user,
            "access": self.access_token,
            "refresh": self.refresh_token,
        }

        return Response(
            api_settings.JWT_SERIALIZER(data, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        self.user = serializer.save()
        self.access_token, self.refresh_token = jwt_encode(self.user)


@extend_schema(responses={status.HTTP_200_OK: api_settings.JWT_SERIALIZER}, summary="Login a user")
class CustomLoginView(PublicEndpoint, LoginView):
    pass


# ---------------------------------------- Password


@extend_schema(responses={status.HTTP_200_OK: RestAuthDetailSerializer}, summary="Change user password")
class CustomPasswordChangeView(PasswordChangeView):
    pass


@extend_schema(summary="Reset user password")
class CustomPasswordResetView(PublicEndpoint, PasswordResetView):
    pass


@extend_schema(summary="Reset user password (confirm)")
class CustomPasswordResetConfirmView(PublicEndpoint, PasswordResetConfirmView):
    pass


# ---------------------------------------- Token


@extend_schema(summary="Verify an access token")
class CustomTokenVerifyView(PublicEndpoint, TokenVerifyView):
    pass


token_refresh_view_cls = get_refresh_view()
CustomTokenRefreshView = extend_schema(summary="Refresh an access token")(token_refresh_view_cls)
