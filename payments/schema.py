import graphene
from rest_framework.exceptions import PermissionDenied

from core.abstract import BaseMutation
from payments.models import Transaction
from payments.object_types import TransactionType


class Deposit(BaseMutation):
    class Arguments:
        amount = graphene.Float(required=True)

    transaction = graphene.Field(TransactionType)

    def mutate(self, info, amount):
        if info.context.user.is_authenticated:
            transaction = Transaction.objects.create(balance=info.context.user.payments_balance, amount=amount)
            return Deposit(transaction=transaction)
        else:
            raise PermissionDenied("You do not have permissions to perform this action.")
