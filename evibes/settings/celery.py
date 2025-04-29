from datetime import timedelta

from evibes.settings import REDIS_PASSWORD

CELERY_BROKER_URL = f"redis://:{REDIS_PASSWORD + '@'}redis:6379/0"
CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD + '@'}redis:6379/0"

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    "update_products_task": {
        "task": "core.tasks.update_products_task",
        "schedule": timedelta(minutes=60),
    },
    "update_orderproducts_task": {
        "task": "core.tasks.update_orderproducts_task",
        "schedule": timedelta(minutes=1),
    },
    "set_default_caches_task": {
        "task": "core.tasks.set_default_caches_task",
        "schedule": timedelta(hours=4),
    },
    "remove_stale_product_images": {
        "task": "core.tasks.remove_stale_product_images",
        "schedule": timedelta(days=1),
    },
    "process_promotions": {
        "task": "core.tasks.process_promotions",
        "schedule": timedelta(hours=2),
    },
}
