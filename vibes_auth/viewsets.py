import logging
import traceback
from contextlib import suppress
from secrets import compare_digest

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from evibes.settings import DEBUG
from vibes_auth.docs.drf.viewsets import USER_SCHEMA
from vibes_auth.models import User
from vibes_auth.serializers import (
    ConfirmPasswordResetSerializer,
    UserSerializer,
)
from vibes_auth.utils.emailing import send_reset_password_email_task

logger = logging.getLogger(__name__)


@extend_schema_view(**USER_SCHEMA)
class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    @method_decorator(ratelimit(key="ip", rate="2/h" if not DEBUG else "888/h"))
    def reset_password(self, request):
        user = None
        with suppress(User.DoesNotExist):
            user = User.objects.get(email=request.data.get("email"))
        if user:
            send_reset_password_email_task.delay(user_pk=user.uuid)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key="ip", rate="2/h" if not DEBUG else "888/h"))
    def upload_avatar(self, request):
        user = self.get_object()
        if request.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]
            user.save()
            return Response(status=status.HTTP_200_OK, data=self.serializer_class(user).data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    @method_decorator(ratelimit(key="ip", rate="2/h" if not DEBUG else "888/h"))
    def confirm_password_reset(self):
        try:
            data = ConfirmPasswordResetSerializer(self.request.data).data

            if not compare_digest(data.get("password"), data.get("confirm_password")):
                return Response(
                    {"error": _("passwords do not match")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            uuid = urlsafe_base64_decode(data.get("uidb64")).decode()
            user = User.objects.get(pk=uuid)

            password_reset_token = PasswordResetTokenGenerator()
            if not password_reset_token.check_token(user, data.get("token")):
                return Response({"error": _("token is invalid!")}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(data.get("password"))
            user.save()
            return Response({"message": _("password reset successfully")}, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(ratelimit(key="ip", rate="3/h" if not DEBUG else "888/h"))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["post"])
    @method_decorator(ratelimit(key="ip", rate="2/h" if not DEBUG else "888/h"))
    def activate(self, request):
        detail = ""
        activation_error = None
        try:
            uuid = urlsafe_base64_decode(request.data.get("uidb64")).decode()
            user = User.objects.nocache().get(pk=uuid)
            if not user.check_token(request.data.get("token")):
                return Response(
                    {"error": _("activation link is invalid!")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.is_active:
                return Response(
                    {"error": _("account already activated!")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_active = True
            user.is_verified = True
            user.save()
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as activation_error:
            user = None
            activation_error = activation_error
            detail = str(traceback.format_exc())
        if user is None:
            if DEBUG:
                raise Exception from activation_error
            return Response(
                {"error": _("activation link is invalid!"), "detail": detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            tokens = RefreshToken.for_user(user)
            response_data = self.serializer_class(user).data
            response_data["refresh"] = str(tokens)
            response_data["access"] = str(tokens.access_token)
            return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        return Response(
            self.get_serializer(self.get_object()).update(instance=self.get_object(), validated_data=request.data).data
        )
