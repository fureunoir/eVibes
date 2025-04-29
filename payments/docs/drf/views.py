from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.docs.drf import error
from payments.serializers import DepositSerializer, TransactionProcessSerializer

DEPOSIT_SCHEMA = {
    "post": extend_schema(
        summary=_("deposit to balance"),
        description=_("deposit some money to balance"),
        request=DepositSerializer,
        responses={
            status.HTTP_201_CREATED: TransactionProcessSerializer,
            status.HTTP_401_UNAUTHORIZED: error,
            status.HTTP_400_BAD_REQUEST: error,
        },
    ),
}
