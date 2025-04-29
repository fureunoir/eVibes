import logging
import traceback

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.docs.drf.views import DEPOSIT_SCHEMA
from payments.gateways import UnknownGatewayError
from payments.models import Transaction
from payments.serializers import DepositSerializer, TransactionProcessSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(**DEPOSIT_SCHEMA)
class DepositView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug(request.__dict__)
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.is_authenticated:
            return Response(data=serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        transaction = Transaction.objects.create(
            balance=request.user.payments_balance, amount=serializer.validated_data["amount"], currency="EUR"
        )

        return Response(TransactionProcessSerializer(transaction).data, status=status.HTTP_303_SEE_OTHER)


@extend_schema(exclude=True)
class CallbackAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug(request.__dict__)
        try:
            gateway = kwargs.get("gateway", "")
            match gateway:
                case "gateway":
                    # Gateway.process_callback(request.data)
                    return Response(status=status.HTTP_200_OK)
                case _:
                    raise UnknownGatewayError(f"Couldn't match '{gateway}' any gateway")
        except Exception as e:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": f"{e}; {traceback.format_exc()}"}
            )
