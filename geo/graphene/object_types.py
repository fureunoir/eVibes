from graphene import InputObjectType, String, relay
from graphene_django import DjangoObjectType

from geo.models import Address, City, Country, PostalCode, Region
from geo.utils import PointScalar


class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        interfaces = (relay.Node,)
        fields = "__all__"


class CityType(DjangoObjectType):
    class Meta:
        model = City
        interfaces = (relay.Node,)
        fields = "__all__"


class RegionType(DjangoObjectType):
    class Meta:
        model = Region
        interfaces = (relay.Node,)
        fields = "__all__"


class PostalCodeType(DjangoObjectType):
    class Meta:
        model = PostalCode
        interfaces = (relay.Node,)
        fields = "__all__"


class AddressType(DjangoObjectType):
    location = PointScalar()

    class Meta:
        model = Address
        interfaces = (relay.Node,)
        exclude = ("user", "billing_address_order", "shipping_address_order")
        filter_fields = ["city__name", "country__name", "postal_code"]


class UnregisteredCustomerAddressInput(InputObjectType):
    billing_customer_city    = String(required=True)
    billing_customer_region  = String(required=True)
    billing_customer_country = String(required=True)
    billing_customer_postal_code  = String(required=True)
    billing_customer_address_line = String(required=True)
