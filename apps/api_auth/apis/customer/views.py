import structlog
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.api_auth.apis.customer.serializers import (
    LoginCustomerResponseSerializer,
    LoginCustomerSerializer,
    UserAuthCustomerSerializer,
)
from apps.api_auth.utils import jwt_encode
from apps.users.choices import UserTypes
from apps.utils.views import PublicEndpoint

logger = structlog.get_logger(__name__)
User = get_user_model()


# Customer Login
# ----------------------------------------------------------------------------------------------------------------------


class AuthCustomerViewSet(PublicEndpoint, GenericViewSet):
    """
    Login using username/email and password.
    Used by the web portals specially for Customers.
    But can be used by any user that has password authentication set-up.
    """

    @extend_schema(responses={200: LoginCustomerResponseSerializer})
    @action(detail=False, methods=["post"], serializer_class=LoginCustomerSerializer)
    @transaction.atomic
    def login(self, request: Request, *args, **kwargs):
        """Login using username/email and password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        # Try to infer the username using the email given
        if email is not None:
            try:
                tmp_user = User.objects.get(email=email, user_type=UserTypes.CUSTOMER)
                username = tmp_user.get_username()
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                pass

        # Authenticate using username and password
        user = authenticate(request, username=username, password=password)
        if user is None:
            raise ValidationError(_("Unable to log in with provided credentials"))
        if user.user_type != UserTypes.CUSTOMER:
            raise ValidationError(_("You are not an Customer, so you cannot use this authentication method"))

        # Encode the user JWT
        access_token, refresh_token = jwt_encode(user)
        user_serializer = UserAuthCustomerSerializer(instance=user)
        res_serializer = LoginCustomerResponseSerializer(
            instance={"user": user_serializer.data, "access": str(access_token), "refresh": str(refresh_token)},
        )
        return Response(status=status.HTTP_200_OK, data=res_serializer.data)
