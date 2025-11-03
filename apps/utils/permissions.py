from django.http import HttpRequest
from rest_framework import permissions

from apps.organizations.models import Organization
from apps.users.choices import EmployeeRoles, UserTypes
from apps.users.models import User
from apps.utils.cache import cache_current_request_property


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


class IsCoach(permissions.DjangoModelPermissions):
    """A coach user (employee with coach access permissions)."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and isinstance(request.user, User)
            and request.user.user_type == UserTypes.EMPLOYEE
            and request.user.emp_permission is not None
            and request.user.emp_permission.coach_access
        )


class EnrolledCustomer(permissions.DjangoModelPermissions):
    """A customer that is enrolled to a branch."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and isinstance(request.user, User)
            and request.user.user_type == UserTypes.CUSTOMER
            and request.user.cus_enrollment is not None
        )


class BranchAdmin(permissions.DjangoModelPermissions):
    """An admin that is enrolled to a branch."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and isinstance(request.user, User)
            and request.user.user_type == UserTypes.EMPLOYEE
            and request.user.emp_organization is not None
        )


class OrganizationAdmin(permissions.BasePermission):
    """An admin that is enrolled to an organization."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and isinstance(request.user, User)
            and request.user.user_type == UserTypes.EMPLOYEE
            and request.user.emp_organization is not None
            and request.user.emp_role == EmployeeRoles.ORG_ADMIN
        )


@cache_current_request_property("current_customer")
def get_current_customer(request: HttpRequest):
    # This should only be called for views protected with EnrolledCustomer
    assert isinstance(request.user, User), "User is not authenticated"
    assert request.user.cus_enrollment is not None, "User is not a customer"
    return request.user.cus_enrollment


@cache_current_request_property("current_emp_organization")
def get_current_emp_organization(request: HttpRequest) -> Organization:
    assert isinstance(request.user, User), "User is not authenticated"

    organization = request.user.emp_organization
    assert organization is not None, "User organization is not set properly"
    return organization


@cache_current_request_property("current_emp_branch_ids")
def get_current_emp_branch_ids(request: HttpRequest):
    assert isinstance(request.user, User), "User is not authenticated"

    organization = request.user.emp_organization
    if organization is None:
        return []
    if request.user.emp_role == EmployeeRoles.ORG_ADMIN:
        return organization.branches.values_list("id", flat=True)
    branch_enrollments = request.user.branch_enrollments_emp.filter(branch__organization=organization)
    return branch_enrollments.values_list("branch_id", flat=True)
