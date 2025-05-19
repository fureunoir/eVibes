import graphene
from django.utils.translation import gettext_lazy as _
from graphene import Float, ObjectType, String
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType

from geo.models import Address


class AddressAutocompleteInput(graphene.InputObjectType):
    q = graphene.String(
        required=True,
        description=_("partial or full address string to search for")
    )
    limit = graphene.Int(
        required=False,
        description=_("maximum number of suggestions to return (1–10)"),
        default_value=5
    )


class AddressSuggestionType(ObjectType):
    display_name = String()
    lat = Float()
    lon = Float()
    address = GenericScalar(
        description=_("the address breakdown as key/value pairs")
    )


class AddressType(DjangoObjectType):
    latitude = graphene.Float(description=_("Latitude (Y coordinate)"))
    longitude = graphene.Float(description=_("Longitude (X coordinate)"))

    class Meta:
        model = Address
        fields = (
            "uuid",
            "street",
            "district",
            "city",
            "region",
            "postal_code",
            "country",
            "raw_data",
            "api_response",
            "user",
        )
        read_only_fields = ("api_response",)

    def resolve_latitude(self, info):
        return self.location.y if self.location else None

    def resolve_longitude(self, info):
        return self.location.x if self.location else None
