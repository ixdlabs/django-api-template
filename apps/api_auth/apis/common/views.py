import structlog
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
    TokenVerifySerializer,
)

from apps.api_auth.apis.common.serializers import UserSerializer
from apps.utils.views import PublicEndpoint

logger = structlog.get_logger(__name__)
User = get_user_model()


# Me
# ----------------------------------------------------------------------------------------------------------------------


class MeCommonViewSet(GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.none()

    @action(detail=False)
    def me(self, request: Request, *args, **kwargs):
        """Get the current user details."""
        serializer = self.get_serializer(instance=self.request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


# Token
# ----------------------------------------------------------------------------------------------------------------------


class TokenCommonViewSet(PublicEndpoint, GenericViewSet):
    @extend_schema(responses={200: TokenVerifySerializer})
    @action(detail=False, methods=["post"], serializer_class=TokenVerifySerializer)
    @transaction.atomic
    def verify(self, request: Request, *args, **kwargs):
        """Verify an access token."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(status=status.HTTP_200_OK)
        except TokenError as e:
            raise InvalidToken(e.args[0])

    @extend_schema(responses={200: TokenRefreshSerializer})
    @action(detail=False, methods=["post"], serializer_class=TokenRefreshSerializer)
    @transaction.atomic
    def refresh(self, request, *args, **kwargs):
        """Refresh an access token."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(status=status.HTTP_200_OK, data=serializer.validated_data)
        except TokenError as e:
            raise InvalidToken(e.args[0])
