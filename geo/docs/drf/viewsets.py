from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.docs.drf import BASE_ERRORS
from geo.serializers import AddressAutocompleteInputSerializer, AddressSerializer, AddressSuggestionSerializer

ADDRESS_SCHEMA = {
    "list": extend_schema(
        summary=_("list all addresses"),
        responses={
            status.HTTP_200_OK: AddressSerializer(many=True),
            **BASE_ERRORS,
        },
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single address"),
        responses={
            status.HTTP_200_OK: AddressSerializer,
            **BASE_ERRORS,
        },
    ),
    "create": extend_schema(
        summary=_("create a new address"),
        request=AddressSerializer,
        responses={
            status.HTTP_201_CREATED: AddressSerializer,
            **BASE_ERRORS,
        },
    ),
    "destroy": extend_schema(
        summary=_("delete an address"),
        responses={
            status.HTTP_204_NO_CONTENT: {},
            **BASE_ERRORS,
        },
    ),
    "update": extend_schema(
        summary=_("update an entire address"),
        request=AddressSerializer,
        responses={
            status.HTTP_200_OK: AddressSerializer,
            **BASE_ERRORS,
        },
    ),
    "partial_update": extend_schema(
        summary=_("partially update an address"),
        request=AddressSerializer,
        responses={
            status.HTTP_200_OK: AddressSerializer,
            **BASE_ERRORS,
        },
    ),
    "autocomplete": extend_schema(
        summary=_("autocomplete address suggestions"),
        request=AddressAutocompleteInputSerializer,
        responses={
            status.HTTP_200_OK: AddressSuggestionSerializer(many=True),
            **BASE_ERRORS,
        },
    ),
}
