import sys

from evibes.settings.base import REDIS_PASSWORD, getenv

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": getenv("CELERY_BROKER_URL", f"redis://:{REDIS_PASSWORD}@redis:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "RETRY_ON_TIMEOUT": True,
            "CONNECTION_POOL_KWARGS": {
                "retry_on_timeout": True,
                "socket_keepalive": True,
            },
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

if any(arg == "celery" for arg in sys.argv):
    CACHEOPS_ENABLED = False
else:
    CACHEOPS_ENABLED = True

    CACHEOPS_REDIS = f"redis://:{REDIS_PASSWORD}@redis:6379/0"

    CACHEOPS = {
        "vibes_auth.user": {"ops": "get", "timeout": 60 * 15},
        "vibes_auth.*": {"ops": {"fetch", "get"}, "timeout": 60 * 60},
        "auth.permission": {"ops": "all", "timeout": 60 * 60},
        "core.*": {"ops": "all", "timeout": 60 * 60},
    }
