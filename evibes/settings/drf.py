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
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        'rest_framework_xml.parsers.XMLParser',
        'rest_framework.parsers.FormParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.generators.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'JSON_UNDERSCOREIZE': {
        'no_underscore_before_number': True,
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=8) if not DEBUG else timedelta(hours=888),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=88),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "SIGNING_KEY": getenv('JWT_SIGNING_KEY', SECRET_KEY),
    "USER_ID_FIELD": "uuid",
    "USER_ID_CLAIM": "user_uuid",

    "AUTH_HEADER_NAME": "HTTP_X-EVIBES-AUTH",
}

SPECTACULAR_B2B_DESCRIPTION = f"""
Welcome to the {CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} B2B API documentation.

The {CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} B2B API is designed to provide seamless integration for merchants selling a wide range of electronics. Through this API, partnered merchants can manage products, orders, and inventory with ease, while accessing real-time stock levels.

## Key Features
- **Product Management:** Easily create, update, and manage your product listings with detailed specifications.
- **Order Processing:** Handle bulk orders efficiently with streamlined operations for merchants.
- **Inventory Management:** Keep track of stock levels in real-time, ensuring smooth fulfillment.
- **Secure Transactions:** Secure and encrypted transactions to protect sensitive business information.
- **Multi-Currency Support:** Expand your market reach with multi-currency transactions.
- **Real-Time Notifications:** Stay updated with instant alerts on stock changes and order statuses.

## Authentication
- Authentication is handled via your merchant token. Include the token in the `X-EVIBES-B2B-AUTH` header of your requests in the format `Bearer <your_token>`.

## I18N
- Apply an `X-Locale` header to use non-default languages. A list of all languages is available at `/config/supported_languages/`.

## Version
Current API version: 1.0.0
"""

SPECTACULAR_PLATFORM_DESCRIPTION = f"""
Welcome to the {CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} Platform API documentation.

The {CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} API is the central hub for managing product listings, monitoring orders, and accessing analytics for your electronics store. It provides RESTful endpoints for managing your store’s backend operations and includes both REST and GraphQL options.

## Key Features
- **Product Catalog:** Manage product details, pricing, and availability.
- **Order Management:** Access detailed order information and process customer requests efficiently.
- **User Roles & Permissions:** Set user roles and permissions for internal management.
- **Custom Integrations:** Connect your system with external platforms through powerful APIs.
- **Detailed Reporting:** Generate comprehensive reports on orders, sales performance, and product data.
- **Real-Time Data:** Get live updates on inventory, pricing, and order statuses.

## Authentication
- Authentication is handled via JWT tokens. Include the token in the `X-EVIBES-AUTH` header of your requests in the format `Bearer <your_token>`.
- Access token lifetime is {SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds() // 60 if not DEBUG else 3600} {'minutes' if not DEBUG else 'hours'}.
- Refresh token lifetime is {SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds() // 3600} hours.
- Refresh tokens are automatically invalidated after usage.

## I18N
- Apply an `X-Locale` header to use non-default languages. A list of all languages is available at `/config/supported_languages/`.

## Version
Current API version: 1.0.0
"""

SPECTACULAR_PLATFORM_SETTINGS = {
    'TITLE': f'{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} API',
    'DESCRIPTION': SPECTACULAR_PLATFORM_DESCRIPTION,
    'VERSION': '1.0.0',
    'SWAGGER_UI_DIST': 'SIDECAR',
    'CAMELIZE_NAMES': True,
    'REDOC_DIST': 'SIDECAR',
    'ENABLE_DJANGO_DEPLOY_CHECK': not DEBUG,
    'SWAGGER_UI_FAVICON_HREF': r"/static/favicon.png",
    'SERVERS': [{'url': f"https://api.{CONSTANCE_CONFIG.get('BASE_DOMAIN')[0]}/", 'description': 'Production Server'},
                {'url': f"http://api.localhost:8000/", 'description': 'Development Server'}, ],
    'CONTACT': {'name': 'Egor "fureunoir" Gorbunov',
                'email': 'contact@fureunoir.com',
                'URL': 'https://t.me/fureunoir'},
}

SPECTACULAR_B2B_SETTINGS = {
    'TITLE': f'{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} API',
    'DESCRIPTION': SPECTACULAR_B2B_DESCRIPTION,
    'VERSION': '1.0.0',
    'SWAGGER_UI_DIST': 'SIDECAR',
    'CAMELIZE_NAMES': True,
    'REDOC_DIST': 'SIDECAR',
    'ENABLE_DJANGO_DEPLOY_CHECK': not DEBUG,
    'SWAGGER_UI_FAVICON_HREF': r"/static/favicon.png",
    'SERVERS': [{'url': f"https://b2b.{CONSTANCE_CONFIG.get('BASE_DOMAIN')[0]}/", 'description': 'Production Server'},
                {'url': f"https://beta.b2b.{CONSTANCE_CONFIG.get('BASE_DOMAIN')[0]}/",
                 'description': 'Beta Solutions Server'}, ],
    'CONTACT': {'name': f'{CONSTANCE_CONFIG.get("COMPANY_NAME")[0]}',
                'email': f'{CONSTANCE_CONFIG.get("EMAIL_HOST_USER")[0]}',
                'URL': f'https://www.{CONSTANCE_CONFIG.get("BASE_DOMAIN")[0]}/help'},
}
