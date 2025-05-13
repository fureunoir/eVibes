from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status

from core.docs.drf import error
from vibes_auth.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
    UserSerializer,
)

TOKEN_OBTAIN_SCHEMA = {
    "post": extend_schema(
        summary=_("obtain a token pair"),
        description=_("obtain a token pair (refresh and access) for authentication."),
        request=TokenObtainPairSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                "TokenObtain",
                fields={
                    "refresh": serializers.CharField(),
                    "access": serializers.CharField(),
                    "user": UserSerializer(),
                },
            ),
            status.HTTP_400_BAD_REQUEST: error,
            status.HTTP_401_UNAUTHORIZED: error,
        },
    )
}

TOKEN_REFRESH_SCHEMA = {
    "post": extend_schema(
        summary=_("refresh a token pair"),
        description=_("refresh a token pair (refresh and access)."),
        request=TokenRefreshSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                "TokenRefreshResponse",
                fields={
                    "refresh": serializers.CharField(),
                    "access": serializers.CharField(),
                    "user": UserSerializer(),
                },
            ),
            status.HTTP_400_BAD_REQUEST: error,
            status.HTTP_401_UNAUTHORIZED: error,
        },
    )
}

TOKEN_VERIFY_SCHEMA = {
    "post": extend_schema(
        summary=_("verify a token"),
        description=_("Verify a token (refresh or access)."),
        request=TokenVerifySerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                "TokenVerifyResponse",
                fields={
                    "token": serializers.CharField(choices=["valid", "no valid"]),
                    "user": UserSerializer(),
                },
            ),
            status.HTTP_400_BAD_REQUEST: error,
            status.HTTP_401_UNAUTHORIZED: error,
        },
    )
}
