from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.dashboard.apis.common.serializers import GlobalSettingSerializer
from apps.dashboard.models import get_current_global_settings, get_organization_settings
from apps.payments.helpers import with_pg_commission
from apps.users.choices import UserTypes


class GlobalSettingsCommonViewSet(GenericViewSet):
    serializer_class = GlobalSettingSerializer
    permission_classes = [AllowAny]

    @action(detail=False)
    def current(self, request, *args, **kwargs):
        global_settings = get_current_global_settings()
        context = self.get_serializer_context()
        if request.user and request.user.is_authenticated and request.user.organization:
            organization_settings = get_organization_settings(request.user.organization)
            context["workout_schedule_price"] = organization_settings.workout_schedule_price
            context["meal_plan_price"] = organization_settings.meal_plan_price
            context["meal_plan_feature"] = organization_settings.meal_plan_feature
            context["workout_feature"] = organization_settings.workout_feature
            context["coaches_feature"] = organization_settings.coaches_feature
            context["sms_marketing_feature"] = organization_settings.sms_marketing_feature
            if request.user.user_type == UserTypes.CUSTOMER:
                context["workout_schedule_price"] = with_pg_commission(context["workout_schedule_price"])
                context["meal_plan_price"] = with_pg_commission(context["meal_plan_price"])

        global_serializer = self.get_serializer(global_settings, context=context)
        return Response(status=status.HTTP_200_OK, data=global_serializer.data)
