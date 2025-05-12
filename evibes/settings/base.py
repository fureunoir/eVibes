import logging
from os import getenv
from pathlib import Path

EVIBES_VERSION = "2.6.0"

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = getenv("SECRET_KEY")
DEBUG = bool(int(getenv("DEBUG")))

ALLOWED_HOSTS = ["*"] if DEBUG else getenv("ALLOWED_HOSTS").split(" ")

CSRF_TRUSTED_ORIGINS = getenv("CSRF_TRUSTED_ORIGINS").split(" ")

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = getenv("CORS_ALLOWED_ORIGINS").split(" ")

    CORS_ALLOW_METHODS = (
        "DELETE",
        "GET",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    )

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "accept-language",
    "content-type",
    "connection",
    "user-agent",
    "authorization",
    "host",
    "x-csrftoken",
    "x-requested-with",
    "x-evibes-auth",
    "baggage",
    "sentry-trace",
    "dnt",
    "sec-fetch-dest",
    "sec-fetch-mode",
    "sec-fetch-site",
    "sec-gpc",
    "origin",
    "referer",
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "SAMEORIGIN"

UNSAFE_CACHE_KEYS = []

SITE_ID = 1

INSTALLED_APPS = [
    "django_daisy",
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.gis",
    "django.contrib.humanize",
    "cacheops",
    "django_hosts",
    "django_celery_beat",
    "django_extensions",
    "django_redis",
    "widget_tweaks",
    "constance",
    "mptt",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_json_widget",
    "django_elasticsearch_dsl",
    "dbbackup",
    "corsheaders",
    "constance.backends.database",
    "django_mailbox",
    "graphene_django",
    "core",
    "geo",
    "payments",
    "vibes_auth",
    "blog",
]

MIDDLEWARE = [
    "evibes.middleware.BlockInvalidHostMiddleware",
    "django_hosts.middleware.HostsRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "evibes.middleware.CustomCommonMiddleware",
    "evibes.middleware.CustomLocaleCommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django_hosts.middleware.HostsResponseMiddleware",
    "djangorestframework_camel_case.middleware.CamelCaseMiddleWare",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "vibes_auth/templates",
            BASE_DIR / "core/templates",
            BASE_DIR / "geo/templates",
            BASE_DIR / "payments/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LANGUAGES = (
    ("en-GB", "English (British)"),
    ("ar-AR", "العربية"),
    ("cs-CZ", "Česky"),
    ("da-DK", "Dansk"),
    ("de-DE", "Deutsch"),
    ("en-US", "English (American)"),
    ("es-ES", "Español"),
    ("fr-FR", "Français"),
    ("hi-IN", "हिंदी"),
    ("it-IT", "Italiano"),
    ("ja-JP", "日本語"),
    ("kk-KZ", "Қазақ"),
    ("nl-NL", "Nederlands"),
    ("pl-PL", "Polska"),
    ("pt-BR", "Português"),
    ("ro-RO", "Română"),
    ("ru-RU", "Русский"),
    ("zh-hans", "简体中文"),
)

LANGUAGE_CODE = "en-GB"

CURRENCIES = (
    ("en-GB", "EUR"),
    ("ar-AR", "AED"),
    ("cs-CZ", "CZK"),
    ("da-DK", "EUR"),
    ("de-DE", "EUR"),
    ("en-US", "USD"),
    ("es-ES", "EUR"),
    ("fr-FR", "EUR"),
    ("hi-IN", "INR"),
    ("it-IT", "EUR"),
    ("ja-JP", "JPY"),
    ("kk-KZ", "KZT"),
    ("nl-NL", "EUR"),
    ("pl-PL", "PLN"),
    ("pt-BR", "EUR"),
    ("ro-RO", "RON"),
    ("ru-RU", "RUB"),
    ("zh-hans", "CNY"),
)

CURRENCY_CODE = dict(CURRENCIES).get(LANGUAGE_CODE)

MODELTRANSLATION_FALLBACK_LANGUAGES = (LANGUAGE_CODE, "en-US", "de-DE")

ROOT_URLCONF = "evibes.urls"

WSGI_APPLICATION = "evibes.wsgi.application"

ASGI_APPLICATION = "evibes.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TIME_ZONE = getenv("TIME_ZONE", "Europe/London")

STATIC_URL = f"https://api.{getenv('BASE_DOMAIN')}/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = f"https://api.{getenv('BASE_DOMAIN')}/media/"
MEDIA_ROOT = BASE_DIR / "media"

AUTH_USER_MODEL = "vibes_auth.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

APPEND_SLASH = True

ROOT_HOSTCONF = "evibes.hosts"
DEFAULT_HOST = "api"
REDIS_PASSWORD = getenv("REDIS_PASSWORD", default="")

INTERNAL_IPS = [
    "127.0.0.1",
]

DAISY_SETTINGS = {
    "SITE_LOGO": "/static/favicon.ico",
    "EXTRA_STYLES": [],
    "EXTRA_SCRIPTS": [],
    "LOAD_FULL_STYLES": True,
    "SHOW_CHANGELIST_FILTER": True,
    "DONT_SUPPORT_ME": True,
    "SIDEBAR_FOOTNOTE": "eVibes by Wiseless",
    "APPS_REORDER": {
        "django_celery_beat": {
            "icon": "fa fa-solid fa-timeline",
            "hide": False,
            "app": "django_celery_beat",
            "priority": 0,
            "apps": "",
        },
        "django_mailbox": {
            "icon": "fa fa-solid fa-envelope",
            "hide": False,
            "app": "django_mailbox",
            "priority": 1,
            "apps": "",
        },
        "geo": {
            "icon": "fa fa-solid fa-globe",
            "hide": False,
            "app": "geo",
            "priority": 2,
            "apps": "",
        },
        "payments": {
            "icon": "fa fa-solid fa-wallet",
            "hide": False,
            "app": "payments",
            "priority": 3,
            "apps": "",
        },
        "blog": {
            "icon": "fa fa-solid fa-book",
            "hide": False,
            "app": "blog",
            "priority": 4,
            "apps": "",
        },
        "core": {
            "icon": "fa fa-solid fa-house",
            "hide": False,
            "app": "core",
            "priority": 5,
            "apps": "",
        },
        "vibes_auth": {
            "icon": "fa fa-solid fa-user",
            "hide": False,
            "app": "vibes_auth",
            "priority": 6,
            "apps": "",
        },
    },
}

if getenv("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    ignore_errors = [
        "flower.views.error.NotFoundErrorHandler",
        "django.http.response.Http404",
        "billiard.exceptions.SoftTimeLimitExceeded",
        "billiard.exceptions.WorkerLostError",
        "core.models.Product.DoesNotExist",
        "core.models.Category.DoesNotExist",
        "core.models.Brand.DoesNotExist",
        "blog.models.Post.DoesNotExist",
    ]

    sentry_sdk.init(
        dsn=getenv("SENTRY_DSN"),
        traces_sample_rate=1.0 if DEBUG else 0.2,
        profiles_sample_rate=1.0 if DEBUG else 0.1,
        integrations=[DjangoIntegration(), LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        ), CeleryIntegration(), RedisIntegration()],
        environment="dev" if DEBUG else "prod",
        debug=DEBUG,
        release=f"evibes@{EVIBES_VERSION}",
        ignore_errors=ignore_errors,
    )

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_HTTPONLY = True

DATA_UPLOAD_MAX_NUMBER_FIELDS = 8888

ADMINS = [('Egor Gorbunov', 'contact@fureunoir.com')]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "dbbackup": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
}
