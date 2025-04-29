from evibes.settings.base import *  # noqa: F403

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": ("%(asctime)s %(log_color)s[%(levelname)s]%(reset)s %(name)s: %(message)s"),
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "bold_green",
                "WARNING": "bold_yellow",
                "ERROR": "bold_red",
                "CRITICAL": "bold_red,bg_white",
            },
        },
        "plain": {
            "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "color",
        },
        "console_production": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "color",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
            "formatter": "plain",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console_debug", "console_production"],
            "level": "DEBUG" if DEBUG else "INFO",  # noqa: F405
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console_debug", "mail_admins"],
            "level": "DEBUG" if DEBUG else "INFO",  # noqa: F405
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console_debug" if DEBUG else "console_production"],  # noqa: F405
            "level": "WARNING",
            "propagate": False,
        },
        "core": {
            "handlers": ["console_debug" if DEBUG else "console_production"],  # noqa: F405
            "level": "DEBUG" if DEBUG else "WARNING",  # noqa: F405
            "propagate": True,
        },
        "django_elasticsearch_dsl": {
            "handlers": ["console_debug" if DEBUG else "console_production"],  # noqa: F405
            "level": "WARNING",
            "propagate": False,
        },
        "celery.app.trace": {
            "handlers": ["console_debug" if DEBUG else "console_production"],  # noqa: F405
            "level": "ERROR",
            "propagate": False,
        },
        "celery.worker.strategy": {
            "handlers": ["console_debug" if DEBUG else "console_production"],  # noqa: F405
            "level": "ERROR",
            "propagate": False,
        },
        "elastic_transport.transport": {
            "handlers": ["console_debug" if DEBUG else "console_production"],  # noqa: F405
            "level": "ERROR",
            "propagate": False,
        },
    },
}
