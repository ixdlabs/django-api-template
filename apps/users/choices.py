from django.db import models


class UserTypes(models.TextChoices):
    UNSET = "UNSET", "Unset"
    CUSTOMER = "CUSTOMER", "Customer"
