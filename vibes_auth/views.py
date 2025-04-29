import logging

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenViewBase

from vibes_auth.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenObtainPairSerializer
    _serializer_class = TokenObtainPairSerializer

    @extend_schema(
        description="Obtain a token pair (refresh and access) for authentication.",
        responses={
            200: inline_serializer(
                name="TokenObtain",
                fields={
                    "refresh": serializers.CharField(),
                    "access": serializers.CharField(),
                    "user": UserSerializer(),
                },
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        name="InvalidCredentials",
                        description="Example of an invalid credentials error",
                        value={
                            "code": 1001,
                            "message": "Invalid credentials were provided.",
                        },
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="TokenExpired",
                        description="Example of an expired token error",
                        value={"code": 1002, "message": "Token is invalid or expired."},
                        response_only=True,
                    )
                ],
            ),
        },
    )
    @method_decorator(ratelimit(key="ip", rate="5/h"))
    def post(self, request, *args, **kwargs):
        logger.debug("Got to super post")
        return super().post(request, *args, **kwargs)


class TokenRefreshView(TokenViewBase):
    serializer_class = TokenRefreshSerializer
    _serializer_class = TokenRefreshSerializer

    @extend_schema(
        description="Refresh a token pair (refresh and access).",
        responses={
            200: inline_serializer(
                name="TokenRefreshResponse",
                fields={
                    "refresh": serializers.CharField(),
                    "access": serializers.CharField(),
                    "user": UserSerializer(),
                },
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        name="InvalidCredentials",
                        description="Example of an invalid credentials error",
                        value={
                            "code": 1001,
                            "message": "Invalid credentials were provided.",
                        },
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="TokenExpired",
                        description="Example of an expired token error",
                        value={"code": 1002, "message": "Token is invalid or expired."},
                        response_only=True,
                    )
                ],
            ),
        },
    )
    @method_decorator(ratelimit(key="ip", rate="5/h"))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenVerifyView(TokenViewBase):
    serializer_class = TokenVerifySerializer
    _serializer_class = TokenVerifySerializer

    @extend_schema(
        description="Verify a token (refresh or access).",
        responses={
            200: inline_serializer(
                name="TokenVerifyResponse",
                fields={
                    "refresh": serializers.CharField(),
                    "access": serializers.CharField(),
                    "user": UserSerializer(),
                },
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        name="InvalidCredentials",
                        description="Example of an invalid credentials error",
                        value={
                            "code": 1001,
                            "message": "Invalid credentials were provided.",
                        },
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        name="TokenExpired",
                        description="Example of an expired token error",
                        value={"code": 1002, "message": "Token is invalid or expired."},
                        response_only=True,
                    )
                ],
            ),
        },
    )
    @method_decorator(ratelimit(key="ip", rate="5/h"))
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_data = serializer.validated_data.pop("user", None)
            return Response({"token": "The token is valid", "user": user_data})
        except TokenError:
            return Response({"detail": "The token is invalid"}, status=status.HTTP_400_BAD_REQUEST)
