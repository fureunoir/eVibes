from evibes.settings.base import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": getenv("POSTGRES_DB"),  # noqa: F405
        "USER": getenv("POSTGRES_USER"),  # noqa: F405
        "PASSWORD": getenv("POSTGRES_PASSWORD"),  # noqa: F405
        "HOST": "database",
        "PORT": 5432,
    }
}
