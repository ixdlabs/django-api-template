from fcm_django.models import FCMDevice
from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationCustomerSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "data",
            "is_broadcast",
            "is_read",
            "created",
            "modified",
        ]

    def get_is_read(self, obj: Notification) -> bool:
        return obj.reads.contains(self.context["request"].user)


class NotificationPushRegistrationCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ["name", "registration_id", "active", "type"]
