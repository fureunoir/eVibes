from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import status
from rest_framework.fields import CharField, DictField, JSONField, ListField

from core.docs.drf import error
from core.serializers import (
    CacheOperatorSerializer,
    ContactUsSerializer,
    LanguageSerializer,
)

CACHE_SCHEMA = {
    "post": extend_schema(
        summary=_("cache I/O"),
        description=_(
            "apply only a key to read permitted data from cache.\napply key, data and timeout with authentication to write data to cache."  # noqa: E501
        ),
        request=CacheOperatorSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer("cache", fields={"data": JSONField()}),
            status.HTTP_400_BAD_REQUEST: error,
        },
    ),
}

LANGUAGE_SCHEMA = {
    "get": extend_schema(
        summary=_("get a list of supported languages"),
        responses={
            status.HTTP_200_OK: LanguageSerializer(many=True),
        },
    )
}

PARAMETERS_SCHEMA = {
    "get": extend_schema(
        summary=_("get application's exposable parameters"),
        responses={status.HTTP_200_OK: inline_serializer("parameters", fields={"key": CharField(default="value")})},
    )
}

CONTACT_US_SCHEMA = {
    "post": extend_schema(
        summary=_("send a message to the support team"),
        request=ContactUsSerializer,
        responses={
            status.HTTP_200_OK: ContactUsSerializer,
            status.HTTP_400_BAD_REQUEST: error,
        },
    )
}

REQUEST_CURSED_URL_SCHEMA = {
    "post": extend_schema(
        summary=_("request a CORSed URL"),
        request=inline_serializer("url", fields={"url": CharField(default="https://example.org")}),
        responses={
            status.HTTP_200_OK: inline_serializer("data", fields={"data": JSONField()}),
            status.HTTP_400_BAD_REQUEST: error,
        },
    )
}

SEARCH_SCHEMA = {
    "get": extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                description="The search query string.",
                required=True,
                type=str,
            )
        ],
        responses={
            200: inline_serializer(
                name="GlobalSearchResponse",
                fields={"results": DictField(child=ListField(child=DictField(child=CharField())))},
            ),
            400: inline_serializer(name="GlobalSearchErrorResponse", fields={"error": CharField()}),
        },
        description=(_("global search endpoint to query across project's tables")),
    )
}
