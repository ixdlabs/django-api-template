from django.db import transaction
from rest_framework import parsers
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.users.apis.coach.serializers import (
    UserCoachSerializer,
    UserPhotoCoachSerializer,
)
from apps.users.choices import UserTypes
from apps.users.models import User
from apps.utils.permissions import IsCoach, IsSameUser


class CoachViewSet(UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsCoach, IsSameUser]
    queryset = User.objects.filter(user_type=UserTypes.EMPLOYEE)
    serializer_class = UserCoachSerializer

    def retrieve(self, request, *args, **kwargs):
        """Return the coach's profile."""
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Replace the coach's profile."""
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
        serializer_class=UserPhotoCoachSerializer,
    )
    @transaction.atomic
    def change_photo(self, request, pk):
        """Change the coach's photo."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
