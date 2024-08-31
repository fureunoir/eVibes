import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evibes.settings')

app = Celery('evibes')

app.conf.update(
    worker_autoscale=(10, 3),
)

app.conf.update(
    worker_prefetch_multiplier=1,
)

app.conf.update(
    worker_max_tasks_per_child=100,
)

app.conf.timezone = 'Europe/Moscow'

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
