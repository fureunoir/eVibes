from rest_framework.fields import BooleanField, CharField, Field, IntegerField, JSONField, ListField, UUIDField
from rest_framework.serializers import ListSerializer, Serializer

from geo.serializers import UnregisteredCustomerAddressSerializer

from .detail import *  # noqa: F403
from .simple import *  # noqa: F403


class CacheOperatorSerializer(Serializer):
    key = CharField(required=True)
    data = JSONField(required=False)
    timeout = IntegerField(required=False)


class ContactUsSerializer(Serializer):
    email = CharField(required=True)
    name = CharField(required=True)
    subject = CharField(required=True)
    phone_number = CharField(required=False)
    message = CharField(required=True)


class LanguageSerializer(Serializer):
    code = CharField(required=True)
    name = CharField(required=True)
    flag = CharField()


class RecursiveField(Field):
    def to_representation(self, value):
        parent = self.parent
        if isinstance(parent, ListSerializer):
            parent = parent.parent

        serializer_class = parent.__class__
        return serializer_class(value, context=self.context).data

    def to_internal_value(self, data):
        return data


class AddOrderProductSerializer(Serializer):
    product_uuid = CharField(required=True)
    attributes = JSONField(required=False, default=dict)


class RemoveOrderProductSerializer(Serializer):
    product_uuid = CharField(required=True)
    attributes = JSONField(required=False, default=dict)


class AddWishlistProductSerializer(Serializer):
    product_uuid = CharField(required=True)


class RemoveWishlistProductSerializer(Serializer):
    product_uuid = CharField(required=True)


class BulkAddWishlistProductSerializer(Serializer):
    product_uuids = ListField(child=CharField(required=True), allow_empty=False, max_length=64)


class BulkRemoveWishlistProductSerializer(Serializer):
    product_uuids = ListField(child=CharField(required=True), allow_empty=False, max_length=64)


class BuyOrderSerializer(Serializer):
    force_balance = BooleanField(required=False, default=False)
    force_payment = BooleanField(required=False, default=False)
    promocode_uuid = CharField(required=False)


class BuyUnregisteredOrderSerializer(Serializer):
    products = ListField(child=AddOrderProductSerializer(), required=True)
    promocode_uuid = UUIDField(required=False)
    customer_name = CharField(required=True)
    customer_email = CharField(required=True)
    customer_phone_number = CharField(required=True)
    billing_customer_address = UnregisteredCustomerAddressSerializer(required=True)
    shipping_customer_address = UnregisteredCustomerAddressSerializer(required=False)
    payment_method = CharField(required=True)
