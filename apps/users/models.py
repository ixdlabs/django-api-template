from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils.models import UUIDModel


class User(UUIDModel, AbstractUser):
    email = models.EmailField("email address", unique=True)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return str(self.get_full_name())
