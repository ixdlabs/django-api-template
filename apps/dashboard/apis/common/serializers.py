import decimal

from rest_framework import serializers

from apps.dashboard.models import GlobalSetting


class GlobalSettingSerializer(serializers.ModelSerializer):
    workout_schedule_price = serializers.SerializerMethodField()
    meal_plan_price = serializers.SerializerMethodField()
    meal_plan_feature = serializers.SerializerMethodField()
    workout_feature = serializers.SerializerMethodField()
    coaches_feature = serializers.SerializerMethodField()
    sms_marketing_feature = serializers.SerializerMethodField()
    sms_cost = serializers.DecimalField(max_digits=8, decimal_places=2, default=decimal.Decimal(0))

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
            "workout_schedule_price",
            "meal_plan_price",
            "meal_plan_feature",
            "workout_feature",
            "coaches_feature",
            "sms_marketing_feature",
            "recurring_payments",
            "sms_cost",
        ]

    def get_workout_schedule_price(self, obj) -> decimal.Decimal:
        return self.context.get("workout_schedule_price", decimal.Decimal("0"))

    def get_meal_plan_price(self, obj) -> decimal.Decimal:
        return self.context.get("meal_plan_price", decimal.Decimal("0"))

    def get_meal_plan_feature(self, obj) -> bool:
        return self.context.get("meal_plan_feature", False)

    def get_workout_feature(self, obj) -> bool:
        return self.context.get("workout_feature", False)

    def get_coaches_feature(self, obj) -> bool:
        return self.context.get("coaches_feature", False)

    def get_sms_marketing_feature(self, obj) -> bool:
        return self.context.get("sms_marketing_feature", False)
