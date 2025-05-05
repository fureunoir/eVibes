from evibes.settings.base import getenv

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"  # Or 'constance.backends.redis.RedisBackend'

CONSTANCE_CONFIG = {
    "PROJECT_NAME": (getenv("PROJECT_NAME"), "Name of the project"),
    "FRONTEND_DOMAIN": (getenv("FRONTEND_DOMAIN"), "Frontend domain name"),
    "BASE_DOMAIN": (getenv("BASE_DOMAIN"), "Base domain name"),
    "COMPANY_NAME": (getenv("COMPANY_NAME"), "Name of the company"),
    "COMPANY_ADDRESS": (getenv("COMPANY_ADDRESS"), "Address of the company"),
    "COMPANY_PHONE_NUMBER": (getenv("COMPANY_PHONE_NUMBER"), "Phone number of the company"),
    "STOCKS_ARE_SINGLE": (getenv("STOCKS_ARE_SINGLE", True), "Designates whether every product has one stock or not"),
    "EMAIL_HOST": (getenv("EMAIL_HOST", "smtp.404.org"), "SMTP host"),
    "EMAIL_PORT": (int(getenv("EMAIL_PORT", "465")), "SMTP port"),
    "EMAIL_USE_TLS": (bool(int(getenv("EMAIL_USE_TLS", 0))), "Use TLS (Specify 0 for No and 1 for Yes)"),
    "EMAIL_USE_SSL": (bool(int(getenv("EMAIL_USE_SSL", 1))), "Use SSL (Specify 0 for No and 1 for Yes)"),
    "EMAIL_HOST_USER": (getenv("EMAIL_HOST_USER", "no-user@fix.this"), "SMTP username"),
    "EMAIL_HOST_PASSWORD": (getenv("EMAIL_HOST_PASSWORD", "SUPERsecretPASSWORD"), "SMTP password"),
    "EMAIL_FROM": (getenv("EMAIL_FROM", "eVibes"), "Mail from option"),
    "PAYMENT_GATEWAY_URL": (getenv("PAYMENT_GATEWAY_URL", "http://404.org"), "Payment gateway URL"),
    "PAYMENT_GATEWAY_TOKEN": (getenv("PAYMENT_GATEWAY_TOKEN", "example token"), "Payment gateway token"),
    "PAYMENT_GATEWAY_MINIMUM": (getenv("PAYMENT_GATEWAY_MINIMUM", 5.0), "Payment gateway minimum amount"),
    "PAYMENT_GATEWAY_MAXIMUM": (getenv("PAYMENT_GATEWAY_MAXIMUM", 500.0), "Payment gateway maximum amount"),
    "EXCHANGE_RATE_API_KEY": (getenv("EXCHANGE_RATE_API_KEY", "example token"), "Exchange rate API key"),
    "OPENAI_API_KEY": (getenv("OPENAI_API_KEY", "example key"), "OpenAI API Key"),
    "ABSTRACT_API_KEY": (
        getenv("ABSTRACT_API_KEY", "example key"),
        "Abstract API Key, if empty - no Abstract features provided",
    ),
    "HTTP_PROXY": (getenv("DJANGO_HTTP_PROXY", "http://username:password@proxy_address:port"), "HTTP Proxy"),
    "DISABLED_COMMERCE": (getenv("DISABLED_COMMERCE", False), "Disable buy functionality"),
}

EXPOSABLE_KEYS = [
    "PROJECT_NAME",
    "BASE_DOMAIN",
    "COMPANY_NAME",
    "COMPANY_ADDRESS",
    "COMPANY_PHONE_NUMBER",
    "EMAIL_HOST_USER",
    "EMAIL_FROM",
    "PAYMENT_GATEWAY_MINIMUM",
    "PAYMENT_GATEWAY_MAXIMUM"
]
