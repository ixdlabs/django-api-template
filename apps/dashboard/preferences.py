from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import BooleanPreference

general = Section("General")


@global_preferences_registry.register
class MaintenanceMode(BooleanPreference):
    name = "maintenance_mode"
    verbose_name = "Maintenance Mode"
    help_text = "Whether the site is in maintenance mode"
    default = False
    section = general
