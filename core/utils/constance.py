from constance import config

from evibes import settings


def set_email_settings():
    settings.EMAIL_HOST = config.EMAIL_HOST
    settings.EMAIL_PORT = config.EMAIL_PORT
    settings.EMAIL_HOST_USER = config.EMAIL_HOST_USER
    settings.EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
    settings.EMAIL_USE_TLS = config.EMAIL_USE_TLS
    settings.EMAIL_USE_SSL = config.EMAIL_USE_SSL
