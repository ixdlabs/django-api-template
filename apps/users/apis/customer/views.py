from django.db import transaction
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.users.apis.customer.serializers import UserCustomerSerializer
from apps.users.choices import UserTypes
from apps.users.models import User
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
