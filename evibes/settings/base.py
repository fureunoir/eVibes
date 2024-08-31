from os import getenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = getenv('SECRET_KEY')
DEBUG = bool(int(getenv('DEBUG')))

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = getenv("ALLOWED_HOSTS").split(" ")

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
    'django_celery_beat',
    'django_extensions',
    'django_redis',
    'constance',
    'adrf',
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
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'evibes.middleware.CustomCommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
    ('en-GB', 'English'),
    ('ru-RU', 'Русский'),
    ('de-DE', 'Deutsch'),
    ('it-IT', 'Italiano'),
    ('es-ES', 'Español'),
    ('nl-NL', 'Nederlands'),
    ('fr-FR', 'Français'),
    ('ro-RO', 'Română'),
    ('pl-PL', 'Polska'),
    ('cs-CZ', 'Česky'),
    ('da-DK', 'Dansk')
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
