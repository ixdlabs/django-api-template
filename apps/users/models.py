from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils.models import UUIDModel

from apps.users.choices import UserTypes

# User
# ----------------------------------------------------------------------------------------------------------------------


class User(UUIDModel, AbstractUser):
    user_type = models.CharField(max_length=15, choices=UserTypes.choices, default=UserTypes.UNSET)
    username = models.CharField(max_length=63, unique=True)
    first_name = models.CharField(max_length=31, blank=True)
    last_name = models.CharField(max_length=31, blank=True)
    email = models.EmailField()

    class Meta:
        ordering = ["-date_joined"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()
