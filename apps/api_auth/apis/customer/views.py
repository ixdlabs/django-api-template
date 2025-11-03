from datetime import timedelta

import structlog
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.api_auth.apis.customer.serializers import (
    LoginResponseCustomerSerializer,
    LoginSendOtpCustomerSerializer,
    LoginSendOtpResponseCustomerSerializer,
    LoginVerifyOtpCustomerSerializer,
    UserAuthCustomerSerializer,
)
from apps.api_auth.models import MobileOtp
from apps.api_auth.utils import jwt_encode
from apps.dashboard.models import get_current_global_settings
from apps.notifications.tasks import (
    send_login_otp_task,
    send_phone_number_change_otp_task,
    send_welcome_message_task,
)
from apps.users.choices import UserTypes
from apps.utils.exceptions import AuthException
from apps.utils.permissions import IsCustomer
from apps.utils.views import PublicEndpoint

logger = structlog.get_logger(__name__)
User = get_user_model()


# Customer Login
# ----------------------------------------------------------------------------------------------------------------------


class AuthCustomerViewSet(PublicEndpoint, GenericViewSet):
    """
    Login using SMS OTP.
    A user can login using the method regardless of whether the user has an account or not.
    If there is a requirement, the user will be created.
    """

    @extend_schema(responses={200: LoginSendOtpResponseCustomerSerializer})
    @action(detail=False, methods=["post"], url_path="send-otp", serializer_class=LoginSendOtpCustomerSerializer)
    @transaction.atomic
    def send_otp(self, request: Request, *args, **kwargs):
        """Send the Login OTP."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        global_settings = get_current_global_settings()
        otp, expiration_at = MobileOtp.generate(phone_number)
        send_login_otp_task.delay(str(phone_number), otp)
        retry_after = timezone.now() + timedelta(seconds=global_settings.otp_resend_wait_duration_seconds)

        res_serializer = LoginSendOtpResponseCustomerSerializer(
            data={"expiration_at": expiration_at, "retry_after": retry_after}
        )
        res_serializer.is_valid(raise_exception=True)
        return Response(res_serializer.data)

    @extend_schema(responses={200: LoginResponseCustomerSerializer})
    @action(detail=False, methods=["post"], url_path="verify-otp", serializer_class=LoginVerifyOtpCustomerSerializer)
    @transaction.atomic
    def verify_otp(self, request: Request, *args, **kwargs):
        """Verify the Login OTP."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        try:
            MobileOtp.verify(phone_number, code)
            logger.info("verified login OTP", phone_number=phone_number)
        except AuthException as e:
            logger.warn(e)
            raise ValidationError(_("Unable to log in with provided OTP"))

        try:
            user = User.objects.get(username=phone_number)
        except User.DoesNotExist:
            logger.info("created user", phone_number=phone_number)
            user = User.objects.create(
                username=phone_number,
                user_type=UserTypes.CUSTOMER,
                phone_number=phone_number,
            )
            # We have to delegate, but wait till txn completed (otherwise user will not be created)
            send_welcome_message_task.delay_on_commit(str(user.id))

        if user.user_type != UserTypes.CUSTOMER:
            raise ValidationError(_("You are not a customer, so you cannot use this authentication method"))

        access_token, refresh_token = jwt_encode(user)
        user_serializer = UserAuthCustomerSerializer(instance=user)
        res_serializer = LoginResponseCustomerSerializer(
            instance={"user": user_serializer.data, "access": str(access_token), "refresh": str(refresh_token)},
        )
        return Response(status=status.HTTP_200_OK, data=res_serializer.data)


# Customer Change Phone Number
# ----------------------------------------------------------------------------------------------------------------------


class AuthCustomerChangePhoneNumberViewSet(GenericViewSet):
    permission_classes = [IsCustomer]

    @extend_schema(responses={200: LoginSendOtpResponseCustomerSerializer})
    @action(detail=False, methods=["post"], url_path="send-otp", serializer_class=LoginSendOtpCustomerSerializer)
    @transaction.atomic
    def send_otp(self, request: Request, *args, **kwargs):
        """Send the Phone Number changing OTP."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        # We will not check if the phone number is already in use.
        # We will simply send the SMS, and after verification, we will say, you already have a different account.
        # However, we will check if this phone number is the phone number of the current user since that is not allowed.
        # Since this user is a customer, checking their user name is enough.
        current_user = self.request.user
        assert isinstance(current_user, User)

        if current_user.get_username() == phone_number:
            raise ValidationError(
                {"phone_number": _("This is the same phone number as your current phone number")},
                code="already_used_phone",
            )

        global_settings = get_current_global_settings()
        otp, expiration_at = MobileOtp.generate(phone_number, user=current_user)
        send_phone_number_change_otp_task.delay(str(phone_number), otp)
        retry_after = timezone.now() + timedelta(seconds=global_settings.otp_resend_wait_duration_seconds)

        res_serializer = LoginSendOtpResponseCustomerSerializer(
            data={"expiration_at": expiration_at, "retry_after": retry_after}
        )
        res_serializer.is_valid(raise_exception=True)
        return Response(res_serializer.data)

    @extend_schema(responses={200: LoginResponseCustomerSerializer})
    @action(detail=False, methods=["post"], url_path="verify-otp", serializer_class=LoginVerifyOtpCustomerSerializer)
    @transaction.atomic
    def verify_otp(self, request: Request, *args, **kwargs):
        """Verify the Phone Number Changing OTP."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        current_user = self.request.user
        assert isinstance(current_user, User)

        try:
            MobileOtp.verify(phone_number, code, user=current_user)
            logger.info("verified phone number changing OTP", phone_number=phone_number)
        except AuthException as e:
            logger.warn(e)
            raise ValidationError(_("Unable to verify provided OTP"))

        if User.objects.filter(username=phone_number).exists():
            raise ValidationError(
                _("Used phone number is already in use, please use a different phone number"),
                code="already_used_phone",
            )

        current_user.phone_number = phone_number
        current_user.save()
        current_user.refresh_from_db()

        # Since user's key details changed (username/phone), we will send a new token
        access_token, refresh_token = jwt_encode(current_user)
        user_serializer = UserAuthCustomerSerializer(instance=current_user)
        res_serializer = LoginResponseCustomerSerializer(
            instance={"user": user_serializer.data, "access": str(access_token), "refresh": str(refresh_token)},
        )
        return Response(status=status.HTTP_200_OK, data=res_serializer.data)
