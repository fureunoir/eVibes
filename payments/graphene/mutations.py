import graphene
from rest_framework.exceptions import PermissionDenied

from core.graphene import BaseMutation
from core.utils.messages import permission_denied_message
from payments.graphene.object_types import TransactionType
from payments.models import Transaction


class Deposit(BaseMutation):
    class Arguments:
        amount = graphene.Float(required=True)

    transaction = graphene.Field(TransactionType)

    def mutate(self, info, amount):
        if info.context.user.is_authenticated:
            transaction = Transaction.objects.create(
                balance=info.context.user.payments_balance, amount=amount, currency="EUR"
            )
            return Deposit(transaction=transaction)
        else:
            raise PermissionDenied(permission_denied_message)
