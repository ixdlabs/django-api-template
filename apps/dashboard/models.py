from django.core.cache import cache
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel

from apps.utils.cache import cache_global_property


@cache_global_property("current_global_settings", timeout=60)
def get_current_global_settings():
    setting, _ = GlobalSetting.objects.get_or_create(is_active=True, defaults={"name": "Default"})
    return setting


# Global Setting
# ----------------------------------------------------------------------------------------------------------------------


class GlobalSetting(UUIDModel, TimeStampedModel, models.Model):
    name = models.CharField(max_length=127, unique=True)
    is_active = models.BooleanField(default=True)
    is_maintenance_mode = models.BooleanField(default=False)
    maintenance_mode_message = models.CharField(max_length=127, blank=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if self.is_active:
            GlobalSetting.objects.exclude(pk=self.pk).update(is_active=False)
        cache.delete("current_global_settings")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
