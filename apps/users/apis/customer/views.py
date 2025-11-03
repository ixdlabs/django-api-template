from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import parsers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.notifications.tasks import send_welcome_to_branch_notification_task
from apps.users.apis.customer.serializers import (
    EnrollCustomerSerializer,
    UserCustomerSerializer,
    UserPhotoCustomerSerializer,
)
from apps.users.choices import UserTypes
from apps.users.models import CustomerEnrollment, User
from apps.utils.permissions import IsCustomer, IsSameUser


class CustomerViewSet(UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsCustomer, IsSameUser]
    queryset = User.objects.filter(user_type=UserTypes.CUSTOMER)
    serializer_class = UserCustomerSerializer

    def retrieve(self, request, *args, **kwargs):
        """Return the customer's profile."""
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Replace the customer's profile."""
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """Partially update selected profile fields."""
        return super().partial_update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["put"],
        url_path="photo",
        parser_classes=[parsers.MultiPartParser],
        serializer_class=UserPhotoCustomerSerializer,
    )
    @transaction.atomic
    def change_photo(self, request, pk):
        """Change the customer's photo."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="enroll", serializer_class=EnrollCustomerSerializer)
    @transaction.atomic
    def enroll(self, request: Request, pk):
        """Enroll the customer to a branch."""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        branch = serializer.validated_data["branch"]

        try:
            enrollment = CustomerEnrollment.objects.get(user=user, branch=branch)
            if enrollment.is_active:
                raise ValidationError(_("You are already enrolled to this branch"), code="already_enrolled")
            enrollment.is_active = True
            enrollment.save()
        except CustomerEnrollment.DoesNotExist:
            enrollment = CustomerEnrollment.objects.create(user=user, branch=branch)
            # We have to delegate, but wait till txn completed (otherwise enrollment will not be created)
        send_welcome_to_branch_notification_task.delay_on_commit(str(enrollment.id))

        return Response(serializer.data)
