from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    ChoicesDropdownFilter,
    RangeDateFilter,
)
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.users.choices import UserTypes
from apps.users.models import CustomerEnrollment, EmployeeEnrollment, EmployeePermission
from apps.utils.admin import header_img, make_display

User = get_user_model()


admin.site.unregister(Group)


# User
# ----------------------------------------------------------------------------------------------------------------------


class CustomerEnrollmentAdminInline(TabularInline):
    model = CustomerEnrollment
    extra = 0
    tab = True
    hide_title = True


class EmployeeEnrollmentAdminInline(TabularInline):
    model = EmployeeEnrollment
    extra = 0
    tab = True
    hide_title = True


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_filter = [
        ("user_type", ChoicesDropdownFilter),
        ("is_staff", BooleanRadioFilter),
        ("is_active", BooleanRadioFilter),
        ("date_joined", RangeDateFilter),
    ]
    list_filter_sheet = False
    list_filter_submit = True
    list_select_related = ["emp_organization", "emp_permission"]
    list_per_page = 10

    search_fields = ["first_name", "last_name", "username", "email", "phone_number"]
    date_hierarchy = "date_joined"

    inlines = [CustomerEnrollmentAdminInline, EmployeeEnrollmentAdminInline]
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    autocomplete_fields = ["emp_organization", "emp_permission"]
    readonly_fields = ["id", "date_joined", "last_login"]
    conditional_fields = {
        "emp_role": "user_type == 'EMPLOYEE'",
        "emp_organization": "user_type == 'EMPLOYEE'",
        "emp_permission": "user_type == 'EMPLOYEE'",
        "password": "user_type != 'CUSTOMER'",
    }
    add_fieldsets = [
        (
            None,
            {
                "fields": (
                    "username",
                    "usable_password",
                    ("password1", "password2"),
                ),
            },
        ),
    ]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "photo",
                    "user_type",
                    "emp_organization",
                    ("emp_role", "emp_permission"),
                    "username",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    ("first_name", "last_name"),
                    ("email", "phone_number"),
                    ("date_of_birth", "gender"),
                    "nic_number",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Address",
            {
                "fields": (("address_line1", "address_line2"), ("address_city", "address_state", "address_zip")),
                "classes": ["tab"],
            },
        ),
        (
            "Health Information",
            {
                "fields": (
                    ("emergency_contact_name", "emergency_contact_phone_number"),
                    "recent_surgery",
                    "recent_surgery_notes",
                    "health_complications",
                    "health_complications_notes",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "MetaData",
            {
                "fields": (
                    "id",
                    ("date_joined", "last_login"),
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
                "classes": ["tab"],
            },
        ),
    ]

    list_display = ["_user", "_user_type", "is_staff", "is_active", "date_joined", "_primary_enrollment"]
    _user = make_display(
        description="user",
        ordering="first_name",
        primary="get_full_name",
        secondary="username",
        image="photo",
        header=True,
    )
    _user_type = make_display(
        description="user type",
        ordering="user_type",
        primary="user_type",
        label={
            UserTypes.CUSTOMER: "success",
            UserTypes.EMPLOYEE: "info",
            UserTypes.UNSET: "warning",
        },
    )

    @display(description="Primary Enrollment", header=True)
    def _primary_enrollment(self, obj):
        if obj.user_type == UserTypes.CUSTOMER:
            if not obj.active_branch_enrollments_cus:
                return ["", "", ""]
            return [
                obj.active_branch_enrollments_cus[0].branch,
                obj.active_branch_enrollments_cus[0].customer_sn,
                *header_img(obj.active_branch_enrollments_cus[0].branch.organization.logo),
            ]
        if obj.user_type == UserTypes.EMPLOYEE:
            if obj.emp_organization is None:
                return ["", "", ""]
            return [obj.emp_organization, obj.get_emp_role_display(), *header_img(obj.emp_organization.logo)]
        return ["", "", ""]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            Prefetch(
                lookup="branch_enrollments_cus",
                queryset=CustomerEnrollment.objects.filter(is_active=True).select_related("branch__organization"),
                to_attr="active_branch_enrollments_cus",
            ),
        )
        return qs


# Enrollments
# ----------------------------------------------------------------------------------------------------------------------


@admin.register(CustomerEnrollment)
class CustomerEnrollmentAdmin(ModelAdmin):
    search_fields = [
        "sn",
        "branch__organization__name",
        "branch__name",
        "user__first_name",
        "user__last_name",
    ]


@admin.register(EmployeeEnrollment)
class EmployeeEnrollmentAdmin(ModelAdmin):
    search_fields = [
        "branch__organization__name",
        "branch__name",
        "user__first_name",
        "user__last_name",
    ]


# Group
# ----------------------------------------------------------------------------------------------------------------------


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


# EmployeePermission
# ----------------------------------------------------------------------------------------------------------------------


@admin.register(EmployeePermission)
class EmployeePermissionAdmin(ModelAdmin):
    list_display = ["organization", "name", "coach_access", "dashboard_financial_access", "created"]
    list_filter = [
        ("coach_access", BooleanRadioFilter),
        ("dashboard_financial_access", BooleanRadioFilter),
    ]
    list_filter_sheet = False
    list_filter_submit = True
    search_fields = ["organization__code", "name"]
    readonly_fields = ["id", "created", "modified"]
    autocomplete_fields = ["organization"]

    fieldsets = [
        (
            None,
            {"fields": ("organization", "name")},
        ),
        (
            "Permissions",
            {"fields": ("coach_access", "dashboard_financial_access"), "classes": ["tab"]},
        ),
        (
            "MetaData",
            {"fields": ("id", "created", "modified"), "classes": ["tab"]},
        ),
    ]
