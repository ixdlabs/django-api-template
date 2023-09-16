from django.contrib.auth.models import AbstractUser
from model_utils.models import UUIDModel


class User(UUIDModel, AbstractUser):
    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return str(self.get_full_name())
