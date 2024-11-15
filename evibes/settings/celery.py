from datetime import timedelta

from evibes.settings.base import *

CELERY_BROKER_URL = getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = getenv('CELERY_TIMEZONE', 'UTC+3')

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    # 'update_products_task': {
    #     'task': 'core.tasks.update_products_task',
    #     'schedule': timedelta(minutes=30),
    # },
    # 'update_promotions_task': {
    #     'task': 'app.tasks.update_promotions_task',
    #     'schedule': timedelta(days=1)
    # },
}
