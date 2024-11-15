from django.core.exceptions import BadRequest
from django.http import Http404
from django.utils.timezone import now

from core.models import Order
from payments.schema import Deposit


def process_order(order_uuid: str) -> Order | Deposit:
    try:
        order = Order.objects.get(uuid=order_uuid)
        if order.user.payments_balance.amount < order.total_price:
            raise BadRequest()

        order.buy_time = now()

        order.user.payments_balance.amount -= order.total_price
        order.user.payments_balance.save()

        order.status = 'CREATED'
        order.save()

        return order

    except Order.DoesNotExist:
        raise Http404
