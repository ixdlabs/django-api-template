from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    ChoicesDropdownFilter,
    RangeDateFilter,
)
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.users.choices import UserTypes
from apps.utils.admin import make_display

User = get_user_model()


admin.site.unregister(Group)


# User
# ----------------------------------------------------------------------------------------------------------------------


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
    list_per_page = 10

    search_fields = ["first_name", "last_name", "username", "email"]
    date_hierarchy = "date_joined"

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    readonly_fields = ["id", "date_joined", "last_login"]
    add_fieldsets = [
        (None, {"fields": ("username", "usable_password", ("password1", "password2"))}),
    ]
    fieldsets = [
        (None, {"fields": ("username", "user_type", "password")}),
        ("Personal Information", {"fields": (("first_name", "last_name"), "email"), "classes": ["tab"]}),
        (
            "MetaData",
            {
                "fields": ("id", ("date_joined", "last_login"), "is_staff", "is_active", "is_superuser"),
                "classes": ["tab"],
            },
        ),
    ]

    list_display = ["_user", "_user_type", "is_staff", "is_active", "date_joined"]
    _user = make_display(
        description="user",
        ordering="first_name",
        primary="get_full_name",
        secondary="username",
        image_text="first_name",
        header=True,
    )
    _user_type = make_display(
        description="user type",
        ordering="user_type",
        primary="user_type",
        label={UserTypes.CUSTOMER: "success", UserTypes.UNSET: "warning"},
    )


# Group
# ----------------------------------------------------------------------------------------------------------------------


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
