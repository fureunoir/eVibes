import os

from celery import Celery

from evibes.settings import REDIS_PASSWORD, TIME_ZONE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evibes.settings")

app = Celery("evibes")

app.conf.update(
    broker_url=f"redis://:{REDIS_PASSWORD}@redis:6379/0",
    result_backend=f"redis://:{REDIS_PASSWORD}@redis:6379/0",
    worker_hijack_root_logger=False,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(name)s: %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(name)s: %(message)s",
    worker_autoscale=(10, 3),
    broker_connection_retry_on_startup=True,
    timezone=TIME_ZONE,
    task_serializer="json",
    result_serializer="json",
    result_compression="zlib",
    accept_content=["json"],
    broker_transport_options={
        "retry_policy": {"interval_start": 0.1, "interval_step": 0.2, "max_retries": 5},
        "visibility_timeout": 3600,
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_soft_time_limit=10800,
    task_time_limit=21600,
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
