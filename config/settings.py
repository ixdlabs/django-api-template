import sys
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import django.conf.locale
import environ  # noqa
import structlog
from firebase_admin import initialize_app

from config.admin import UNFOLD_ADMIN_UI
from config.firebase import CustomFirebaseCredentials

# Build paths inside the project like this: ROOT_DIR / 'subdir'.
# Default apps directory is set to ROOT_DIR/apps
ROOT_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT_DIR / "apps"

# Configure django environ
# OS environment variables take precedence over variables from .env
env = environ.Env()
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    env.read_env(str(ROOT_DIR / ".env"))

# ---------------------------------------------------------- General ---------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", True)
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY", default="local")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
DEFAULT_ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=DEFAULT_ALLOWED_HOSTS)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
# Local time zone. http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Asia/Colombo"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(ROOT_DIR / "locale")]
# https://docs.djangoproject.com/en/3.1/ref/settings/#append-slash
APPEND_SLASH = True
# Languages
LANGUAGES = [
    ("en", "english"),
    ("si", "sinhala"),
]
LANG_INFO = {**django.conf.locale.LANG_INFO, "si": {"code": "si", "name": "Sinhala"}}
django.conf.locale.LANG_INFO = LANG_INFO

# ---------------------------------------------------------- Databases -------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///sqlite.db"),
}
# Connection pooling for better DB performance
# https://docs.djangoproject.com/en/5.2/ref/settings/#conn-max-age
DATABASES["default"]["CONN_MAX_AGE"] = 600
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ---------------------------------------------------------- Urls ------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------- Apps ------------------------------------------------------
DJANGO_ADMIN_THEME_APPS = [
    "unfold",
]
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "unfold.contrib.filters",
    "django.contrib.humanize",
    "django.forms",
]
I18N_OVERRIDE_APPS = [
    "apps.i18n.rest_framework_locale",
    "apps.i18n.phonenumber_field_locale",
]
THIRD_PARTY_APPS = [
    "django_structlog",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
    "django_celery_results",
    "anymail",
    "drf_standardized_errors",
    "import_export",
    "phonenumber_field",
    "fcm_django",
]
LOCAL_APPS = [
    "apps.dashboard.apps.DashboardConfig",
    "apps.api_auth.apps.ApiAuthConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.users.apps.UsersConfig",
]
CLEANUP_APPS = ["django_cleanup.apps.CleanupConfig"]

# ---------------------------------------------------------- Authentication --------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"

# ---------------------------------------------------------- Passwords -------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------- Middleware ------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
    "apps.dashboard.middlewares.MaintenanceModeMiddleware",
]

# ---------------------------------------------------------- Static ----------------------------------------------------
# Static files will be stored in '.static' directoy.
# Media files will be stored in '.media' directory.
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR / ".static")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_DIRS = [ROOT_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = str(ROOT_DIR / ".media")
# https://docs.djangoproject.com/en/5.2/ref/settings/#storages
# Following is the default value, we redeclare it so the next storages can update it.
STORAGES: dict[str, Any] = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# ---------------------------------------------------------- AWS Static ------------------------------------------------
# Static and Media files config in AWS environment.
USE_AWS_S3 = env.bool("USE_AWS_S3", default=False)
if USE_AWS_S3:
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    THIRD_PARTY_APPS += ["storages"]
    AWS_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
            "querystring_auth": True,
            "object_parameters": {"CacheControl": "max-age=86400"},
        },
    }

# ------------------------------------------------------ Azure Blob Static ---------------------------------------------
# Static and Media files config in Azure environment.
USE_AZURE_BLOB = env.bool("USE_AZURE_BLOB", default=False)
if USE_AZURE_BLOB:
    # https://django-storages.readthedocs.io/en/latest/backends/azure.html
    THIRD_PARTY_APPS += ["storages"]
    AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME", default="")
    AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY", default="")
    AZURE_CONTAINER = env("AZURE_CONTAINER_NAME", default="media")
    STORAGES["default"] = {
        "BACKEND": "config.storages.CustomAzureStorage",
        "OPTIONS": {
            "account_name": AZURE_ACCOUNT_NAME,
            "account_key": AZURE_ACCOUNT_KEY,
            "azure_container": AZURE_CONTAINER,
            "overwrite_files": False,
            "expiration_secs": 7200,  # 2 hours
        },
    }

# ------------------------------------------------------ Whitenoise ----------------------------------------------------
# https://whitenoise.readthedocs.io/en/stable/django.html
# This should come after django security middleware.
if env.bool("USE_WHITENOISE", default=False):
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }

# ---------------------------------------------------------- Templates -------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                (
                    "django.template.loaders.filesystem.Loader",
                    [str(ROOT_DIR / "templates")],
                ),
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
        },
    }
]
# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# ---------------------------------------------------------- Security --------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# ---------------------------------------------------------- Email -----------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
# We will disable this since errors are monitored independently
ADMINS: list[str] = []
MANAGERS = ADMINS

# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="mail@example.com")
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
USE_RESEND = env.bool("USE_RESEND", default=False)
USE_MAILCAPTURE = env.bool("USE_MAILCAPTURE", default=False)
if USE_RESEND:
    # https://anymail.dev/en/stable/esps/resend/
    RESEND_API_KEY = env.str("RESEND_API_KEY")
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
    ANYMAIL = {"RESEND_API_KEY": RESEND_API_KEY}
elif USE_MAILCAPTURE:
    # MailHog: https://github.com/mailhog/MailHog
    # Mailpit: https://github.com/axllent/mailpit
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# ---------------------------------------------------------- Admin -----------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"

# ---------------------------------------------------------- Logging ---------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# For tips on struct log
# See https://hodovi.cc/blog/django-development-and-production-logging/

DJANGO_LOG_LEVEL = env.str("DJANGO_LOG_LEVEL", "DEBUG")
DJANGO_REQUEST_LOG_LEVEL = env.str("DJANGO_REQUEST_LOG_LEVEL", "INFO")
DJANGO_CELERY_LOG_LEVEL = env.str("DJANGO_CELERY_LOG_LEVEL", "INFO")
DJANGO_DATABASE_LOG_LEVEL = env.str("DJANGO_DATABASE_LOG_LEVEL", "CRITICAL")

DEFAULT_LOGGER_HANDLER = "console" if DEBUG else "json"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
        },
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=False),
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "event", "logger"]),
        },
    },
    "handlers": {
        # Important notes regarding handlers.
        #
        # 1. Make sure you use handlers adapted for your project.
        # These handlers configurations are only examples for this library.
        # See python's logging.handlers: https://docs.python.org/3/library/logging.handlers.html
        #
        # 2. You might also want to use different logging configurations depending of the environment.
        # Different files (local.py, tests.py, production.py, ci.py, etc.) or only conditions.
        # See https://docs.djangoproject.com/en/dev/topics/settings/#designating-the-settings
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored_console",
        },
        "json": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
        "null": {
            "class": "logging.NullHandler",
        },
        "otel": {
            "class": "config.otel.OtelLogHandler",
            "formatter": "plain_console",
        },
    },
    "loggers": {
        # DB logs
        "django.db.backends": {
            "handlers": [DEFAULT_LOGGER_HANDLER],
            "level": DJANGO_DATABASE_LOG_LEVEL,
        },
        # Silence django's default logging
        "django.server": {
            "handlers": ["null"],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["null"],
            "propagate": False,
        },
        # Structlog loggers
        "django_structlog": {
            "handlers": [DEFAULT_LOGGER_HANDLER],
            "level": DJANGO_LOG_LEVEL,
        },
        "django_structlog.middlewares": {
            "handlers": [DEFAULT_LOGGER_HANDLER],
            "level": DJANGO_REQUEST_LOG_LEVEL,
            "propagate": False,
        },
        "django_structlog.celery": {
            "handlers": [DEFAULT_LOGGER_HANDLER],
            "level": DJANGO_CELERY_LOG_LEVEL,
        },
        "root": {
            "handlers": [DEFAULT_LOGGER_HANDLER],
            "level": DJANGO_LOG_LEVEL,
        },
    },
}
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
DJANGO_STRUCTLOG_CELERY_ENABLED = True

# ---------------------------------------------------------- Redis -----------------------------------------------------

# If redis URL is set, we will use it for caching
REDIS_URL = env.str("REDIS_URL", default=None)
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }

# ---------------------------------------------------------- Django Rest Framework -------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": env.int("DJANGO_PAGINATION_PAGE_SIZE", 10),
    "MAX_PAGE_SIZE": env.int("DJANGO_PAGINATION_MAX_PAGE_SIZE", 25),
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "DEFAULT_SCHEMA_CLASS": "config.schema.CustomAutoSchema",
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=180),
}
# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
# Enable CORS to all API endpoints.
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_URLS_REGEX = r"^/(admin-api|api-auth|api/v1)/.*$"
# Custom exception handler
# https://drf-standardized-errors.readthedocs.io/en/latest/customization.html#handle-a-non-drf-exception
DRF_STANDARDIZED_ERRORS = {"EXCEPTION_HANDLER_CLASS": "config.exceptions.CustomExceptionHandler"}

# ---------------------------------------------------------- DRF Spectacular OpenAPI Documentation ---------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Backend API",
    "DESCRIPTION": "Django API Template",
    "VERSION": "0.0.1",
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"\/(api|admin\-api)\/v[0-9]",
    "SORT_OPERATION_PARAMETERS": True,
    "CONTACT": {"name": "kdsuneraavinash", "email": "sunera@ixdlabs.com"},
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.SessionAuthentication"],
    "AUTHENTICATION_WHITELIST": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "POSTPROCESSING_HOOKS": ["drf_standardized_errors.openapi_hooks.postprocess_schema_enums"],
    "ENUM_NAME_OVERRIDES": {
        # Explanation: https://github.com/tfranzel/drf-spectacular/issues/482#issuecomment-904998597
        "ValidationErrorEnum": "drf_standardized_errors.openapi_serializers.ValidationErrorEnum",
        "ClientErrorEnum": "drf_standardized_errors.openapi_serializers.ClientErrorEnum",
        "ServerErrorEnum": "drf_standardized_errors.openapi_serializers.ServerErrorEnum",
        "ParseErrorCodeEnum": "drf_standardized_errors.openapi_serializers.ParseErrorCodeEnum",
        "ErrorCode401Enum": "drf_standardized_errors.openapi_serializers.ErrorCode401Enum",
        "ErrorCode403Enum": "drf_standardized_errors.openapi_serializers.ErrorCode403Enum",
        "ErrorCode404Enum": "drf_standardized_errors.openapi_serializers.ErrorCode404Enum",
        "ErrorCode405Enum": "drf_standardized_errors.openapi_serializers.ErrorCode405Enum",
        "ErrorCode406Enum": "drf_standardized_errors.openapi_serializers.ErrorCode406Enum",
        "ErrorCode415Enum": "drf_standardized_errors.openapi_serializers.ErrorCode415Enum",
        "ErrorCode429Enum": "drf_standardized_errors.openapi_serializers.ErrorCode429Enum",
        "ErrorCode500Enum": "drf_standardized_errors.openapi_serializers.ErrorCode500Enum",
        "CurrentMembershipTimeStateEnum": "apps.memberships.choices.MembershipTimeStates",
        "RequestStateEnum": "apps.workouts.choices.RequestStates",
        "PaymentMethodEnum": "apps.payments.choices.PaymentMethods",
        "WorkoutLevelAssignmentEnum": "apps.workouts.choices.WorkoutLevelAssignments",
        "WorkoutGenderAssignmentEnum": "apps.workouts.choices.WorkoutGenderAssignments",
        "PaymentBackendEnum": "apps.dashboard.choices.PaymentBackends",
        "GenderEnum": "apps.users.choices.Genders",
        "SmsGroupGenderEnum": "apps.notifications.choices.SmsGroupGenders",
        "OrderStateEnum": "apps.products.choices.OrderStates",
    },
}

# ---------------------------------------------------------- Django Toolbar --------------------------------------------
USE_DEBUG_TOOLBAR = env.bool("USE_DEBUG_TOOLBAR", default=DEBUG)
if USE_DEBUG_TOOLBAR:
    THIRD_PARTY_APPS += ["debug_toolbar"]
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    TEMPLATES += [
        {
            "NAME": "DEBUG_TOOLBAR_TEMPLATES",
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,  # type: ignore
        }
    ]
    DEBUG_TOOLBAR_CONFIG = {"UPDATE_ON_FETCH": True}

# ---------------------------------------------------------- Django Extensions -----------------------------------------
USE_DJANGO_EXTENSIONS = env.bool("USE_DJANGO_EXTENSIONS", default=DEBUG)
if USE_DJANGO_EXTENSIONS:
    THIRD_PARTY_APPS += ["django_extensions"]

# ---------------------------------------------------------- Django Import Export --------------------------------------

IMPORT_EXPORT_IMPORT_PERMISSION_CODE = "add"
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = "view"
IMPORT_EXPORT_SKIP_ADMIN_CONFIRM = False

# ---------------------------------------------------------- Django Admin Interface ------------------------------------
LIST_PER_PAGE = 20
UNFOLD = UNFOLD_ADMIN_UI

# ---------------------------------------------------------- Celery ----------------------------------------------------

USE_CELERY = env.bool("USE_CELERY", default=True)
if USE_CELERY:
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_CACHE_BACKEND = "default"
    CELERY_RESULT_BACKEND = "django-db"
    CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=None)
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
    CELERY_TASK_ALWAYS_EAGER = False
else:
    # Following will make the celery tasks always run in eager mode.
    # So tasks will not be submitted to the worker.
    CELERY_TASK_ALWAYS_EAGER = True

# ---------------------------------------------------------- Firebase --------------------------------------------------

# Setup instructions: https://fcm-django.readthedocs.io/en/latest/
FCM_DJANGO_SETTINGS = {
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": True,
}

# This is required for the demo page
FIREBASE_DEMO_WEB_CONFIG_JSON = env.json("FIREBASE_DEMO_WEB_CONFIG_JSON", default={})
FIREBASE_DEMO_WEB_VAPID_KEY = env.str("FIREBASE_DEMO_WEB_VAPID_KEY", default="")

# We will initialize firebase only if the service account json is set
FIREBASE_SERVICE_ACCOUNT_JSON = env.str("FIREBASE_SERVICE_ACCOUNT_JSON", default=None)
if FIREBASE_SERVICE_ACCOUNT_JSON is not None:
    initialize_app(CustomFirebaseCredentials(FIREBASE_SERVICE_ACCOUNT_JSON))

# ---------------------------------------------------------- Zeal ------------------------------------------------------
# https://github.com/taobojlen/django-zeal
# Detects N+1 queries, but since this has a high performance impact, this should only run in tests
if "test" in sys.argv:
    THIRD_PARTY_APPS += ["zeal"]
    MIDDLEWARE.append("zeal.middleware.zeal_middleware")
    ZEAL_SHOW_ALL_CALLERS = True


# ----------------------------------------------------------- Installed Apps -------------------------------------------
# This is placed last to make sure the changes done in settings file is all reflected here
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = (
    I18N_OVERRIDE_APPS + DJANGO_ADMIN_THEME_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + CLEANUP_APPS
)
