import graphene
from graphene import relay
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType

from payments.models import Balance, Transaction


class TransactionType(DjangoObjectType):
    process = GenericScalar()

    def resolve_process(self, info):
        return self.process

    class Meta:
        model = Transaction
        exclude = ("balance",)
        interfaces = (relay.Node,)
        filter_fields = ["is_active"]


class BalanceType(DjangoObjectType):
    transaction_set = graphene.List(lambda: TransactionType)

    class Meta:
        model = Balance
        fields = "__all__"
        interfaces = (relay.Node,)
        filter_fields = ["is_active"]

    def resolve_transaction_set(self, info):
        return self.transaction_set.all() or []
