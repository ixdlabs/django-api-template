from typing import Any

from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import sensitive_post_parameters_m
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api_auth.serializers import RegisterSerializer

user_model = get_user_model()


@extend_schema(auth=[], responses={status.HTTP_201_CREATED: api_settings.JWT_SERIALIZER})
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

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
