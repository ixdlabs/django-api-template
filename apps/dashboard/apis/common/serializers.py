from rest_framework import serializers

from apps.dashboard.models import GlobalSetting


class GlobalSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSetting
        fields = ["is_maintenance_mode", "maintenance_mode_message"]
