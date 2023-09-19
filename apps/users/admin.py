from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from config.admin import custom_admin_site

User = get_user_model()


@admin.register(User, site=custom_admin_site)
class UserAdmin(BaseUserAdmin):
    pass
