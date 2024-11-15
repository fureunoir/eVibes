import logging
import warnings

from evibes.settings.base import *
from evibes.settings.constance import CONSTANCE_CONFIG

warnings.filterwarnings(
    "ignore",
    message="StreamingHttpResponse must consume synchronous iterators in order to serve them asynchronously",
    category=UserWarning,
    module="django.http.response",
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'stunning': {
            'format': '[{asctime}] [{levelname:^8}] {name}: {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'stunning',
        },
        'console_production': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'stunning',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'stunning',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console', 'console_production'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': True,
        },
        'geo': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': True,
        },
        'vibes_auth': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': True,
        },
        'payments': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': True,
        },
        'hypercorn.error': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

logger = logging.getLogger(str(CONSTANCE_CONFIG.get('PROJECT_NAME')))
