from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.teemill import process_order
from evibes.settings import logger
from payments.models import Transaction
from payments.utils.currencies import update_currencies_to_euro


@extend_schema(exclude=True)
class CallbackAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            transaction = Transaction.objects.get(uuid=request.data.get('payment_session').get('order_id'))
            amount = request.data.get('transaction').get('amount')

            if request.data.get('transaction').get('currency').upper() != 'EUR':
                amount = update_currencies_to_euro(
                    request.data.get('transaction').get('currency'),
                    amount)

            if not transaction.process.get('success', False):
                transaction.balance.amount += float(amount)
                transaction.balance.save()
                transaction.process['success'] = True
                transaction.save()
                if transaction.order:
                    transaction.order.status = 'DELIVERING'
                    transaction.order.save()
                    process_order(transaction.order.uuid)

        except Transaction.DoesNotExist:
            logger.warning(f"Transaction {request.data.get('payment_session').get('order_id')} not found")
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
