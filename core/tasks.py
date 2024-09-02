from celery.app import shared_task

from core.utils.prepaidforge import fetch_prepaid_forge


@shared_task
def update_products_task():
    return fetch_prepaid_forge()
