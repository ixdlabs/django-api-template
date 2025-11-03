from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.dashboard.apis.common.serializers import GlobalSettingSerializer
from apps.dashboard.models import get_current_global_settings


class GlobalSettingsCommonViewSet(GenericViewSet):
    serializer_class = GlobalSettingSerializer
    permission_classes = [AllowAny]

    @action(detail=False)
    def current(self, request, *args, **kwargs):
        global_settings = get_current_global_settings()
        context = self.get_serializer_context()

        global_serializer = self.get_serializer(global_settings, context=context)
        return Response(status=status.HTTP_200_OK, data=global_serializer.data)
