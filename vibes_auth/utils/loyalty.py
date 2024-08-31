from celery import shared_task
from django.utils import timezone
from django.utils.crypto import get_random_string

from app.models import PromoCode, User, Order


@shared_task
def give_user_loyalty_promo(user: User) -> PromoCode | None:
    if (sum(order.total_price for order in Order.objects.filter(user=user)) / 200) > 1 & (
            sum(order.total_price for order in Order.objects.filter(user=user)) // 200) > PromoCode.objects.filter(
            user=user, discount_amount=5.00).count():
        return PromoCode.objects.create(user=user, discount_amount=5.0, start_time=timezone.now(),
                                        end_time=timezone.now(), code=get_random_string(20).upper())
