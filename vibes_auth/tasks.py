from celery import shared_task

from core.models import Order, Wishlist
from vibes_auth.models import User


@shared_task
def create_pending_order(user_uuid):
    try:
        user = User.objects.get(uuid=user_uuid)
        Order.objects.create(user=user, status="PENDING")
        return True, f"Successfully created order for {user_uuid}"
    except User.DoesNotExist:
        return False, f"Bad uuid was given: {user_uuid}"


@shared_task
def create_wishlist(user_uuid):
    try:
        user = User.objects.get(uuid=user_uuid)
        Wishlist.objects.create(user=user)
        return True, f"Successfully created wishlist for {user_uuid}"
    except User.DoesNotExist:
        return False, f"Bad uuid was given: {user_uuid}"
