from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from fcm_django.api.rest_framework import DeviceViewSetMixin
from fcm_django.api.rest_framework import IsOwner as FcmOwner
from fcm_django.models import FCMDevice
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.notifications.apis.customer.serializers import (
    NotificationCustomerSerializer,
    NotificationPushRegistrationCustomerSerializer,
)
from apps.notifications.models import Notification
from apps.utils.permissions import IsCustomer
from apps.utils.serializers import DetailSerializer


class NotificationCustomerViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationCustomerSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(mode_push=True)
        return qs.filter(Q(recipient_users=self.request.user) | Q(is_broadcast=True))

    def list(self, request, *args, **kwargs):
        """List all the user's notifications."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Return a user's notification."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(responses={200: DetailSerializer}, request=None)
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def read(self, request, *args, **kwargs):
        """Mark a notification as read."""
        notification: Notification = self.get_object()
        notification.reads.add(request.user)
        return Response({"detail": _("Notification marked as read")})

    @extend_schema(responses={200: DetailSerializer}, request=None)
    @action(detail=False, methods=["post"], url_path="read-all")
    @transaction.atomic
    def read_all(self, request, *args, **kwargs):
        """Mark all notifications as read."""
        notifications = self.get_queryset()
        request.user.read_notifications.add(*notifications)
        return Response({"detail": _("All notifications marked as read")})


class NotificationFcmDeviceViewSet(DeviceViewSetMixin, CreateModelMixin, GenericViewSet):
    queryset = FCMDevice.objects.all()
    serializer_class = NotificationPushRegistrationCustomerSerializer
    permission_classes = [IsCustomer, FcmOwner]

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def register(self, request, *args, **kwargs):
        """Register the device for FCM notifications"""
        return super().create(request, *args, **kwargs)

    @extend_schema(exclude=True)
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        raise NotImplementedError()
