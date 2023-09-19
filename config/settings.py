from collections import OrderedDict
from pathlib import Path

import environ  # noqa
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: ROOT_DIR / 'subdir'.
# Default apps directory is set to ROOT_DIR/apps
ROOT_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT_DIR / "apps"

# Configure django environ
# OS environment variables take precedence over variables from .env
env = environ.Env()
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
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
# Local time zone. http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
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
    ("en", _("English")),
]

# ---------------------------------------------------------- Databases -------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///sqlite.db"),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ---------------------------------------------------------- Urls ------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------- Apps ------------------------------------------------------
DJANGO_ADMIN_THEME_APPS = [
    "admin_interface",
    "colorfield",
]
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "dj_rest_auth",
    "drf_spectacular",
    "django_filters",
    "constance",
    "constance.backends.database",
    "anymail",
    "drf_standardized_errors",
    "import_export",
]
LOCAL_APPS = [
    "apps.dashboard.apps.DashboardConfig",
    "apps.api_auth.apps.ApiAuthConfig",
    "apps.users.apps.UsersConfig",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_ADMIN_THEME_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

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

# ---------------------------------------------------------- AWS Static ------------------------------------------------
# Static and Media files config in AWS environment.
USE_AWS_S3 = env.bool("USE_AWS_S3", default=False)
if USE_AWS_S3:
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    INSTALLED_APPS += ["storages"]
    AWS_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    DEFAULT_FILE_STORAGE = "config.storages.MediaRootS3Boto3Storage"
    MEDIA_URL = "https://%s.s3.%s.amazonaws.com/%s/media/" % (
        AWS_STORAGE_BUCKET_NAME,
        AWS_S3_REGION_NAME,
        AWS_STORAGE_BUCKET_NAME,
    )

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
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
# TODO: Change this to server domain.
DEFAULT_FROM_EMAIL = "mail@notifications.example.com"
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
USE_MAILGUN = env.bool("USE_MAILGUN", default=False)
USE_MAIL_HOG = env.bool("USE_MAIL_HOG", default=False)
if USE_MAILGUN:
    # https://anymail.readthedocs.io/en/stable/esps/mailgun/
    MAILGUN_API_KEY = env.str("MAILGUN_API_KEY")
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    ANYMAIL = {"MAILGUN_API_KEY": MAILGUN_API_KEY}
elif USE_MAIL_HOG:
    # MailHog: https://github.com/mailhog/MailHog
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# ---------------------------------------------------------- Admin -----------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""ixdlabs""", "developer@ixdlabs.lk")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# ---------------------------------------------------------- Logging ---------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
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
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_standardized_errors.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
}
# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
# Enable CORS to all API endpoints.
CORS_ALLOW_ALL_ORIGINS = True
CORS_URLS_REGEX = r"^/(admin-api|api-auth|api/v1)/.*$"

# ---------------------------------------------------------- Django Rest Auth ------------------------------------------
# https://dj-rest-auth.readthedocs.io/en/latest/configuration.html
REST_AUTH = {
    "OLD_PASSWORD_FIELD_ENABLED": True,
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "access_token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",
    "JWT_AUTH_HTTPONLY": False,
    "USER_DETAILS_SERIALIZER": "apps.users.serializers.UserSerializer",
}

# ---------------------------------------------------------- DRF Spectacular OpenAPI Documentation ---------------------
# TODO: Change project details.
SPECTACULAR_SETTINGS = {
    "TITLE": "Example API",
    "DESCRIPTION": "Example Backend API",
    "VERSION": "0.0.1",
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"\/(api|admin\-api)\/v[0-9]",
    "SORT_OPERATION_PARAMETERS": True,
    "CONTACT": {"name": "kdsuneraavinash", "email": "sunera@ixdlabs.com"},
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.SessionAuthentication"],
    "AUTHENTICATION_WHITELIST": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "POSTPROCESSING_HOOKS": ["drf_standardized_errors.openapi_hooks.postprocess_schema_enums"],
    "ENUM_NAME_OVERRIDES": {
        "ValidationErrorEnum": "drf_standardized_errors.openapi_serializers.ValidationErrorEnum.values",
        "ClientErrorEnum": "drf_standardized_errors.openapi_serializers.ClientErrorEnum.values",
        "ServerErrorEnum": "drf_standardized_errors.openapi_serializers.ServerErrorEnum.values",
        "ErrorCode401Enum": "drf_standardized_errors.openapi_serializers.ErrorCode401Enum.values",
        "ErrorCode403Enum": "drf_standardized_errors.openapi_serializers.ErrorCode403Enum.values",
        "ErrorCode404Enum": "drf_standardized_errors.openapi_serializers.ErrorCode404Enum.values",
        "ErrorCode405Enum": "drf_standardized_errors.openapi_serializers.ErrorCode405Enum.values",
        "ErrorCode406Enum": "drf_standardized_errors.openapi_serializers.ErrorCode406Enum.values",
        "ErrorCode415Enum": "drf_standardized_errors.openapi_serializers.ErrorCode415Enum.values",
        "ErrorCode429Enum": "drf_standardized_errors.openapi_serializers.ErrorCode429Enum.values",
        "ErrorCode500Enum": "drf_standardized_errors.openapi_serializers.ErrorCode500Enum.values",
    },
}

# ---------------------------------------------------------- Django Constance ------------------------------------------
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_CONFIG: OrderedDict = OrderedDict()

# ---------------------------------------------------------- Django Toolbar --------------------------------------------
USE_DEBUG_TOOLBAR = env.bool("USE_DEBUG_TOOLBAR", default=DEBUG)
if USE_DEBUG_TOOLBAR:
    INSTALLED_APPS += ["debug_toolbar"]
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    TEMPLATES += [
        {
            "NAME": "DEBUG_TOOLBAR_TEMPLATES",
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,  # type: ignore
        }
    ]

# ---------------------------------------------------------- Sentry ----------------------------------------------------
USE_SENTRY = env.bool("USE_SENTRY", default=False)
if USE_SENTRY:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=env.str("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=env.float("SENTRY_SAMPLE_RATE", 0.1),
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

# ---------------------------------------------------------- Django Extensions -----------------------------------------
USE_DJANGO_EXTENSIONS = env.bool("USE_DJANGO_EXTENSIONS", default=DEBUG)
if USE_DJANGO_EXTENSIONS:
    INSTALLED_APPS += ["django_extensions"]

# ---------------------------------------------------------- Django Import Export --------------------------------------

IMPORT_EXPORT_IMPORT_PERMISSION_CODE = "add"
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = "view"
IMPORT_EXPORT_SKIP_ADMIN_CONFIRM = False

# ---------------------------------------------------------- Django Admin Interface ------------------------------------
ADMIN_MODELS = [
    ["Authentication/Authorization", ("Group", "User")],
    ["Site Settings", ("Theme", "Site", "Config")],
]
