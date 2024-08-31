from datetime import timedelta

from evibes.settings.constance import CONSTANCE_CONFIG
from evibes.settings.base import *

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'evibes.pagination.CustomPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=88),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "SIGNING_KEY": SECRET_KEY,
    "USER_ID_FIELD": "uuid",
    "USER_ID_CLAIM": "user_uuid",
}

SPECTACULAR_SETTINGS = {
    'TITLE': CONSTANCE_CONFIG.get('PROJECT_NAME'),
    'DESCRIPTION': "This API documentation is used to describe available HTTP methods on several endpoints serving "
                   "products information on www.itoption.com\nAccess Token Lifetime is 8 minutes.\n"
                   "Refresh Token Lifetime is 88 hours. Refresh Tokens are blacklisted after usage.",
    'CONTACT': {'name': 'Egor "fureunoir" Gorbunov',
                'email': 'contact@fureunoir.com',
                'URL': 'https://t.me/fureunoir'},
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'ENABLE_DJANGO_DEPLOY_CHECK': not DEBUG,
    'SERVERS': [{'url': f"https://{CONSTANCE_CONFIG.get('BACKEND_DOMAIN')}/", 'description': 'Production Server'},
                {'url': f"http://127.0.0.1/", 'description': 'Development Server'},]
}
