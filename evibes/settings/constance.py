from evibes.settings.base import *

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'  # Or 'constance.backends.redis.RedisBackend'

CONSTANCE_CONFIG = {
    'PROJECT_NAME': (getenv('PROJECT_NAME'), 'Name of the project'),
    'FRONTEND_DOMAIN': (getenv('FRONTEND_DOMAIN'), 'Frontend domain URL'),
    'BACKEND_DOMAIN': (getenv('BACKEND_DOMAIN'), 'Backend domain URL'),
    'COMPANY_NAME': (getenv('COMPANY_NAME'), 'Name of the company'),
    'COMPANY_ADDRESS': (getenv('COMPANY_ADDRESS'), 'Address of the company'),
    'COMPANY_PHONE_NUMBER': (getenv('COMPANY_PHONE_NUMBER'), 'Phone number of the company'),

    'EMAIL_HOST': (getenv("EMAIL_HOST", "smtp.404.org"), 'SMTP host'),
    'EMAIL_PORT': (int(getenv("EMAIL_PORT", "465")), 'SMTP port'),
    'EMAIL_USE_TLS': (bool(int(getenv("EMAIL_USE_TLS", 0))), 'Use TLS (Specify 0 for No and 1 for Yes)'),
    'EMAIL_USE_SSL': (bool(int(getenv("EMAIL_USE_SSL", 1))), 'Use SSL (Specify 0 for No and 1 for Yes)'),
    'EMAIL_HOST_USER': (getenv("EMAIL_HOST_USER", "no-user@fix.this"), 'SMTP username'),
    'EMAIL_HOST_PASSWORD': (getenv("EMAIL_HOST_PASSWORD", "SUPERsecretPASSWORD"), 'SMTP password'),

    'PAYMENT_GATEWAY_URL': (getenv('PAYMENT_GATEWAY_URL', "http://404.org"), 'Payment gateway URL'),
    'PAYMENT_GATEWAY_TOKEN': (getenv('PAYMENT_GATEWAY_TOKEN', "example token"), 'Payment gateway token'),

    'OPENAI_API_KEY': (getenv('OPENAI_API_KEY', "example key"), 'OpenAI API Key'),

    'TELEGRAM_BOT_TOKEN': (getenv('TELEGRAM_BOT_TOKEN', "example token"), 'Telegram bot token'),
}
