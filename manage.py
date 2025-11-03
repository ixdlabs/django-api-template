#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from config.otel import setup_open_telemetry


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    # Setup open telemetry only if running via "runserver --noreload"
    if sys.argv[1] == "runserver" and "--noreload" in sys.argv:
        setup_open_telemetry("fitconnect-backend")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
