import logging

from django.core.cache import cache
from django.test import TestCase

from apps.dashboard.models import GlobalSetting, get_current_global_settings


class GlobalSettingModelTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_can_create_global_setting(self):
        setting = GlobalSetting.objects.create(name="Default Setting")
        self.assertTrue(setting.is_active)
        self.assertEqual(setting.name, "Default Setting")

    def test_only_one_global_setting_can_be_active(self):
        setting1 = GlobalSetting.objects.create(name="Setting1", is_active=True)
        setting2 = GlobalSetting.objects.create(name="Setting2", is_active=True)
        setting1.refresh_from_db()
        self.assertFalse(setting1.is_active)
        self.assertTrue(setting2.is_active)

    def test_global_setting_str_returns_name(self):
        setting = GlobalSetting.objects.create(name="MySetting")
        self.assertEqual(str(setting), "MySetting")

    def test_save_clears_cache(self):
        setting = GlobalSetting.objects.create(name="CacheTest")
        cache.set("current_global_settings", setting)
        setting.save()
        self.assertIsNone(cache.get("current_global_settings"))

    def test_get_current_global_settings_creates_if_not_exist(self):
        cache.delete("current_global_settings")
        setting = get_current_global_settings()
        self.assertIsInstance(setting, GlobalSetting)
        self.assertTrue(setting.is_active)
