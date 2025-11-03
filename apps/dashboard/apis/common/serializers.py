from rest_framework import serializers

from apps.dashboard.models import GlobalSetting


class GlobalSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSetting
        fields = [
            "otp_digit_count",
            "android_latest_version",
            "android_minimum_required_version",
            "android_update_url",
            "ios_latest_version",
            "ios_minimum_required_version",
            "ios_update_url",
            "recurring_payments",
        ]
