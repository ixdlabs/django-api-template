from rest_framework import permissions

from apps.users.choices import UserTypes
from apps.users.models import User


class IsSameUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsCustomer(permissions.DjangoModelPermissions):
    """A customer that is enrolled to a branch."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and isinstance(request.user, User)
            and request.user.user_type == UserTypes.CUSTOMER
        )
