from rest_framework.fields import FloatField, JSONField
from rest_framework.serializers import ModelSerializer, Serializer

from payments.models import Transaction


class DepositSerializer(Serializer):
    amount = FloatField(required=True)


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionProcessSerializer(ModelSerializer):
    process = JSONField(required=True)

    class Meta:
        model = Transaction
        fields = ("process",)
