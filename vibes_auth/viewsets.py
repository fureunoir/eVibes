import logging
from secrets import compare_digest

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from vibes_auth.models import User
from vibes_auth.serializers import (
    ActivateEmailSerializer,
    ConfirmPasswordResetSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)
from vibes_auth.utils.emailing import send_reset_password_email_task

logger = logging.getLogger(__name__)


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

    @extend_schema(
        description="Reset a user's password by sending a reset password email.",
        request=ResetPasswordSerializer(),
        responses={200: {}, 400: {"description": "Email does not exist"}},
    )
    @action(detail=False, methods=["post"])
    @method_decorator(ratelimit(key="ip", rate="2/h"))
    def reset_password(self, request):
        try:
            user = User.objects.get(email=request.data.get("email"))
        except User.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "Email does not exist"},
            )

        send_reset_password_email_task.delay(user_pk=user.uuid)
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        description="Handle avatar upload for a user.",
        methods=["PUT"],
        responses={
            200: UserSerializer(),
            400: {"description": "Invalid Request"},
            403: {"description": "Bad credentials"},
        },
    )
    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key="ip", rate="2/h"))
    def upload_avatar(self, request):
        user = self.get_object()
        if request.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]
            user.save()
            return Response(status=status.HTTP_200_OK, data=self.serializer_class(user).data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Confirm a password reset for a user.",
        request=ConfirmPasswordResetSerializer(),
        responses={
            200: {"description": "Password reset successfully"},
            400: {"description": "Invalid uid!"},
        },
    )
    @action(detail=False, methods=["post"])
    @method_decorator(ratelimit(key="ip", rate="2/h"))
    def confirm_password_reset(self):
        try:
            data = ConfirmPasswordResetSerializer(self.request.data).data

            if not compare_digest(data.get("password"), data.get("confirm_password")):
                return Response(
                    {"error": "Passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            uuid = urlsafe_base64_decode(data.get("uidb64")).decode()
            user = User.objects.get(pk=uuid)

            password_reset_token = PasswordResetTokenGenerator()
            if not password_reset_token.check_token(user, data.get("token")):
                return Response({"error": "Token is invalid!"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(data.get("password"))
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(str(e))
            return Response({"error": "Invalid uuid!"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UserSerializer,
        description="Create a new user. An activation email will be sent after creation.",
        responses={201: UserSerializer()},
    )
    @method_decorator(ratelimit(key="ip", rate="3/h"))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.save()
        # send_email_confirmation.delay(user.pk)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        description="Activate a user's account.",
        responses={
            200: UserSerializer(),
            400: {"description": "Activation link is invalid!"},
        },
        request=ActivateEmailSerializer(),
    )
    @action(detail=False, methods=["post"])
    @method_decorator(ratelimit(key="ip", rate="2/h"))
    def activate(self, request):
        try:
            uuid = urlsafe_base64_decode(request.data.get("uidb64")).decode()
            user = User.objects.get(pk=uuid)
            if not user.check_token(request.data.get("token")):
                return Response(
                    {"error": "Activation link is invalid!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.is_active:
                return Response(
                    {"error": "Account already activated!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_active = True
            user.is_verified = True
            user.save()
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            user = None
            logger.error(str(e))
        if user is None:
            return Response(
                {"error": "Activation link is invalid!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            tokens = RefreshToken.for_user(user)
            response_data = self.serializer_class(user).data
            response_data["refresh"] = str(tokens)
            response_data["access"] = str(tokens.access_token)
            return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(description="Retrieve a user's details.")
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        description="Update a user's details.",
        request=UserSerializer,
    )
    def update(self, request, pk=None, *args, **kwargs):
        return Response(
            self.get_serializer(self.get_object()).update(instance=self.get_object(), validated_data=request.data).data
        )
