from os import getenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = getenv('SECRET_KEY')
DEBUG = bool(int(getenv('DEBUG')))

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = getenv("ALLOWED_HOSTS").split(" ")

CSRF_TRUSTED_ORIGINS = getenv("CSRF_TRUSTED_ORIGINS").split(" ")

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = getenv("CORS_ALLOWED_ORIGINS").split(" ")

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'accept-language',
    'content-type',
    'connection',
    'user-agent',
    'authorization',
    'host',
    'x-csrftoken',
    'x-requested-with',
    'baggage',
    'sentry-trace',
    'dnt',
    'sec-fetch-dest',
    'sec-fetch-mode',
    'sec-fetch-site',
    'sec-gpc',
    'origin',
    'referer',
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'SAMEORIGIN'

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.gis',
    'django_hosts',
    'django_celery_beat',
    'django_extensions',
    'django_redis',
    'widget_tweaks',
    'constance',
    'parler',
    'mptt',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'django_json_widget',
    'corsheaders',
    'constance.backends.database',
    'django_mailbox',
    'graphene_django',
    'core',
    'geo',
    'payments',
    'vibes_auth',
]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'evibes.middleware.CustomCommonMiddleware',
    'evibes.middleware.CustomLocaleCommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
    'djangorestframework_camel_case.middleware.CamelCaseMiddleWare',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'vibes_auth/templates',
            BASE_DIR / 'core/templates',
            BASE_DIR / 'geo/templates',
            BASE_DIR / 'payments/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LANGUAGES = [
    ('en-us', 'American English'),
    ('en-gb', 'English'),
    ('ru-ru', 'Русский'),
    ('de-de', 'Deutsch'),
    ('it-it', 'Italiano'),
    ('es-es', 'Español'),
    ('nl-nl', 'Nederlands'),
    ('fr-fr', 'Français'),
    ('ro-ro', 'Română'),
    ('pl-pl', 'Polska'),
    ('cs-cz', 'Česky'),
    ('da-dk', 'Dansk')
]

ROOT_URLCONF = 'evibes.urls'

WSGI_APPLICATION = 'evibes.wsgi.application'

ASGI_APPLICATION = 'evibes.asgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TIME_ZONE = getenv('TIME_ZONE', 'Europe/Moscow')

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'vibes_auth.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

APPEND_SLASH = True

ROOT_HOSTCONF = 'evibes.hosts'
DEFAULT_HOST = 'api'

INTERNAL_IPS = [
    '127.0.0.1',
]

if getenv("SENTRY_DSN"):
    import sentry_sdk

    sentry_sdk.init(
        dsn=getenv('SENTRY_DSN'),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
