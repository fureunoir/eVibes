from rest_framework.fields import (
    BooleanField,
    CharField,
    DictField,
    Field,
    FloatField,
    IntegerField,
    JSONField,
    ListField,
    UUIDField,
)
from rest_framework.serializers import ListSerializer, Serializer

from core.models import Address

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


class BulkAddOrderProductsSerializer(Serializer):
    products = ListField(child=AddOrderProductSerializer(), required=True)


class RemoveOrderProductSerializer(Serializer):
    product_uuid = CharField(required=True)
    attributes = JSONField(required=False, default=dict)


class BulkRemoveOrderProductsSerializer(Serializer):
    products = ListField(child=RemoveOrderProductSerializer(), required=True)


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
    shipping_address_uuid = CharField(required=False)
    billing_address_uuid = CharField(required=False)


class BuyUnregisteredOrderSerializer(Serializer):
    products = ListField(child=AddOrderProductSerializer(), required=True)
    promocode_uuid = UUIDField(required=False)
    customer_name = CharField(required=True)
    customer_email = CharField(required=True)
    customer_phone_number = CharField(required=True)
    billing_customer_address_uuid = CharField(required=False)
    shipping_customer_address_uuid = CharField(required=False)
    payment_method = CharField(required=True)


class BuyAsBusinessOrderSerializer(Serializer):
    products = ListField(child=AddOrderProductSerializer(), required=True)
    business_inn = CharField(required=True)
    business_email = CharField(required=True)
    business_phone_number = CharField(required=True)
    billing_business_address_uuid = CharField(required=False)
    shipping_business_address_uuid = CharField(required=False)
    payment_method = CharField(required=True)


class AddressAutocompleteInputSerializer(Serializer):
    q = CharField(required=True)
    limit = IntegerField(required=False, min_value=1, max_value=10, default=5)


class AddressSuggestionSerializer(Serializer):
    display_name = CharField()
    lat = FloatField()
    lon = FloatField()
    address = DictField(child=CharField())


class AddressSerializer(ModelSerializer):  # noqa: F405
    latitude = FloatField(source="location.y", read_only=True)
    longitude = FloatField(source="location.x", read_only=True)

    class Meta:
        model = Address
        fields = [
            "uuid",
            "street",
            "district",
            "city",
            "region",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "raw_data",
            "api_response",
            "user",
        ]
        read_only_fields = [
            "latitude",
            "longitude",
            "raw_data",
            "api_response",
        ]


class AddressCreateSerializer(ModelSerializer):  # noqa: F405
    raw_data = CharField(
        write_only=True,
        max_length=512,
    )
    address_line_1 = CharField(
        write_only=True,
        max_length=128,
        required=False
    )
    address_line_2 = CharField(
        write_only=True,
        max_length=128,
        required=False
    )

    class Meta:
        model = Address
        fields = ["raw_data"]

    def create(self, validated_data):
        raw = validated_data.pop("raw_data")
        user = None
        if self.context["request"].user.is_authenticated:
            user = self.context["request"].user
        return Address.objects.create(raw_data=raw, user=user, **validated_data)
