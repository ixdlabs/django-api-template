from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel


class User(UUIDModel, AbstractUser):
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
