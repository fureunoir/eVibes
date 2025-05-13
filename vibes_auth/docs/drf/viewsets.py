from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.docs.drf import BASE_ERRORS
from vibes_auth.serializers import (
    ActivateEmailSerializer,
    ConfirmPasswordResetSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)

USER_SCHEMA = {
    "create": extend_schema(
        summary=_("create a new user"),
        responses={status.HTTP_201_CREATED: UserSerializer, **BASE_ERRORS},
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a user's details"),
        responses={status.HTTP_200_OK: UserSerializer, **BASE_ERRORS},
    ),
    "update": extend_schema(
        summary=_("update a user's details"),
        request=UserSerializer,
        responses={status.HTTP_200_OK: UserSerializer, **BASE_ERRORS},
    ),
    "destroy": extend_schema(
        summary=_("delete a user"),
        responses={status.HTTP_204_NO_CONTENT: {}, **BASE_ERRORS},
    ),
    "reset_password": extend_schema(
        summary=_("reset a user's password by sending a reset password email"),
        request=ResetPasswordSerializer,
        responses={
            status.HTTP_200_OK: {},
            **BASE_ERRORS
        },
    ),
    "upload_avatar": extend_schema(
        summary=_("handle avatar upload for a user"),
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: {"description": "Invalid Request"},
            status.HTTP_403_FORBIDDEN: {"description": "Bad credentials"},
            **BASE_ERRORS
        },
    ),
    "confirm_password_reset": extend_schema(
        summary=_("confirm a user's password reset"),
        request=ConfirmPasswordResetSerializer,
        responses={
            status.HTTP_200_OK: {"description": "Password reset successfully"},
            status.HTTP_400_BAD_REQUEST: {"description": _("passwords do not match")},
            **BASE_ERRORS
        },
    ),
    "activate": extend_schema(
        summary=_("activate a user's account"),
        request=ActivateEmailSerializer,
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: {"description": _("activation link is invalid or account already activated")},
            **BASE_ERRORS
        },
    ),
}
