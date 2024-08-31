import graphene
from graphene_django import DjangoObjectType

from payments.models import Balance, Transaction


class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction
        exclude = ('balance',)


class BalanceType(DjangoObjectType):
    transaction_set = graphene.List(lambda: TransactionType)

    class Meta:
        model = Balance
