import logging

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import (
    extend_schema_view,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenViewBase

from evibes.settings import DEBUG
from vibes_auth.docs.drf.views import TOKEN_OBTAIN_SCHEMA, TOKEN_REFRESH_SCHEMA, TOKEN_VERIFY_SCHEMA
from vibes_auth.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(**TOKEN_OBTAIN_SCHEMA)
class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenObtainPairSerializer
    _serializer_class = TokenObtainPairSerializer

    @method_decorator(ratelimit(key="ip", rate="10/h" if not DEBUG else "888/h"))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema_view(**TOKEN_REFRESH_SCHEMA)
class TokenRefreshView(TokenViewBase):
    serializer_class = TokenRefreshSerializer
    _serializer_class = TokenRefreshSerializer

    @method_decorator(ratelimit(key="ip", rate="10/h" if not DEBUG else "888/h"))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema_view(**TOKEN_VERIFY_SCHEMA)
class TokenVerifyView(TokenViewBase):
    serializer_class = TokenVerifySerializer
    _serializer_class = TokenVerifySerializer

    @method_decorator(ratelimit(key="ip", rate="10/h" if not DEBUG else "888/h"))
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_data = serializer.validated_data.pop("user", None)
            return Response({"token": _("the token is valid"), "user": user_data})
        except TokenError:
            return Response({"detail": _("the token is invalid")}, status=status.HTTP_400_BAD_REQUEST)
