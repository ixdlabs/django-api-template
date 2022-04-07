from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj == request.user


class IsAuthorizedStaffUser(permissions.DjangoModelPermissions):
    """A staff user with the required permissions."""

    def has_permission(self, request, view):
        return (request.user and request.user.is_staff) and super().has_permission(request, view)
