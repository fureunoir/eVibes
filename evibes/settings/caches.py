CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "RETRY_ON_TIMEOUT": True,
            "CONNECTION_POOL_KWARGS": {
                "retry_on_timeout": True,
                "socket_keepalive": True,
            },
            # "IGNORE_EXCEPTIONS": True,   # Uncomment to ignore exceptions (use with caution)
        }
    }
}