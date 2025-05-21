import logging
from hmac import compare_digest

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import BadRequest, PermissionDenied
from django.db import IntegrityError
from django.http import Http404
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from graphene import UUID, Boolean, Field, List, String
from graphene.types.generic import GenericScalar
from graphene_file_upload.scalars import Upload
from rest_framework.exceptions import ValidationError

from core.graphene import BaseMutation
from core.utils.messages import permission_denied_message
from evibes.settings import LANGUAGE_CODE
from vibes_auth.graphene.object_types import UserType
from vibes_auth.models import User
from vibes_auth.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
)
from vibes_auth.utils.emailing import send_reset_password_email_task
from vibes_auth.validators import is_valid_email, is_valid_phone_number

logger = logging.getLogger(__name__)


class CreateUser(BaseMutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)
        confirm_password = String(required=True)
        last_name = String()
        first_name = String()
        phone_number = String()
        is_subscribed = Boolean()
        language = String()
        referrer = String(required=False, description=_("the user's b64-encoded uuid who referred the new user to us."))

    success = Boolean()

    def mutate(
            self,
            info,
            email,
            password,
            confirm_password,
            last_name=None,
            first_name=None,
            phone_number=None,
            is_subscribed=None,
            language=None,
            **kwargs,
    ):
        try:
            if compare_digest(password, confirm_password):
                User.objects.create_user(
                    email=email,
                    password=password,
                    last_name=last_name,
                    first_name=first_name,
                    phone_number=phone_number,
                    is_subscribed=is_subscribed if is_subscribed else False,
                    language=language if language else LANGUAGE_CODE,
                    attributes={"referrer": kwargs.get("referrer", "")} if kwargs.get("referrer", "") else {},
                )
                return CreateUser(success=True)
            else:
                return CreateUser(success=False)
        except IntegrityError:
            return CreateUser(success=True)
        except Exception as e:
            raise BadRequest(str(e))


class UpdateUser(BaseMutation):
    class Arguments:
        uuid = UUID(required=True)
        email = String(required=False)
        phone_number = String(required=False)
        password = String(required=False)
        confirm_password = String(required=False)
        is_verified = Boolean(required=False)
        first_name = String(required=False)
        last_name = String(required=False)
        language = String(required=False)
        is_active = Boolean(required=False)
        is_staff = Boolean(required=False)
        user_permissions = List(String)
        groups = List(String)
        attributes = GenericScalar(required=False)

    user = Field(UserType)

    def mutate(self, info, uuid, **kwargs):
        try:
            user = User.objects.get(uuid=uuid)

        except User.DoesNotExist:
            name = "User"
            raise Http404(_(f"{name} does not exist: {uuid}"))

        if not (info.context.user.has_perm("vibes_auth.change_user") or info.context.user == user):
            raise PermissionDenied(permission_denied_message)

        email = kwargs.get("email")

        if email is not None and not is_valid_email(email):
            raise BadRequest(_("malformed email"))

        phone_number = kwargs.get("phone_number")

        if phone_number is not None and not is_valid_phone_number(phone_number):
            raise BadRequest(_(f"malformed phone number: {phone_number}"))

        password = kwargs.get("password", "")
        confirm_password = kwargs.get("confirm_password", "")

        if not compare_digest(password, "") and compare_digest(password, confirm_password):
            user.set_password(password)
            user.save()

        attribute_pairs = kwargs.pop("attributes", "")

        if attribute_pairs:
            for attribute_pair in attribute_pairs.split(";"):
                if "-" in attribute_pair:
                    attr, value = attribute_pair.split("-", 1)
                    if not user.attributes:
                        user.attributes = {}
                    user.attributes.update({attr: value})
                else:
                    raise BadRequest(_(f"Invalid attribute format: {attribute_pair}"))

        for attr, value in kwargs.items():
            if attr == "password" or attr == "confirm_password":
                continue
            if attr not in [
                "groups",
                "user_permissions",
                "is_verified",
                "is_staff",
                "is_active",
                "is_superuser",
            ] or info.context.user.has_perm("vibes_auth.change_user"):
                setattr(user, attr, value)

            user.save()

        return UpdateUser(user=user)


class DeleteUser(BaseMutation):
    class Arguments:
        email = String()
        uuid = UUID()

    success = Boolean()

    def mutate(self, info, uuid=None, email=None):
        if info.context.user.has_perm("vibes_auth.delete_user"):
            try:
                if uuid is not None:
                    User.objects.get(uuid=uuid).delete()
                elif email is not None:
                    User.objects.get(email=email).delete()
                else:
                    raise BadRequest("uuid or email must be specified")
                return DeleteUser(success=True)
            except User.DoesNotExist:
                raise Http404(f"User with the given uuid: {uuid} or email: {email} does not exist.")
        raise PermissionDenied(permission_denied_message)


class ObtainJSONWebToken(BaseMutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    user = Field(UserType)
    refresh_token = String(required=True)
    access_token = String(required=True)

    def mutate(self, info, email, password):
        serializer = TokenObtainPairSerializer(data={"email": email, "password": password})
        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(email=email)
            return ObtainJSONWebToken(
                user=user,
                refresh_token=serializer.validated_data["refresh"],
                access_token=serializer.validated_data["access"],
            )
        except Exception as e:
            raise PermissionDenied(f"invalid credentials provided: {e!s}")


class RefreshJSONWebToken(BaseMutation):
    class Arguments:
        refresh_token = String(required=True)

    access_token = String()
    user = Field(UserType)
    refresh_token = String()

    def mutate(self, info, refresh_token):
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
            return RefreshJSONWebToken(
                access_token=serializer.validated_data["access"],
                refresh_token=serializer.validated_data["refresh"],
                user=User.objects.get(uuid=serializer.validated_data["user"]["uuid"]),
            )
        except Exception as e:
            raise PermissionDenied(f"invalid refresh token provided: {e!s}")


class VerifyJSONWebToken(BaseMutation):
    class Arguments:
        token = String(required=True)

    token_is_valid = Boolean()
    user = Field(UserType)

    def mutate(self, info, token):
        serializer = TokenVerifySerializer(data={"token": token})
        try:
            serializer.is_valid(raise_exception=True)
            user_uuid = serializer.validated_data["user"]["uuid"]
            user = User.objects.get(pk=user_uuid)
            return VerifyJSONWebToken(
                token_is_valid=True,
                user=user,
            )
        except ValidationError:
            return VerifyJSONWebToken(token_is_valid=False, user=None)


class ActivateUser(BaseMutation):
    class Arguments:
        uid = String(required=True)
        token = String(required=True)

    success = Boolean()

    def mutate(self, info, uid, token):
        try:
            token = urlsafe_base64_decode(token).decode()
            uuid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uuid)

            if not user.check_token(token):
                raise BadRequest(_("activation link is invalid!"))

            if user.is_active:
                raise BadRequest(_("account already activated..."))

            user.is_active = True
            user.is_verified = True
            user.save()

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            raise BadRequest(_(f"something went wrong: {e!s}"))

        return ActivateUser(success=True)


class ResetPassword(BaseMutation):
    class Arguments:
        email = String(required=True)

    success = Boolean()

    def mutate(self, info, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        send_reset_password_email_task.delay(user_pk=user.uuid)

        return ResetPassword(success=True)


class ConfirmResetPassword(BaseMutation):
    class Arguments:
        uid = String(required=True)
        token = String(required=True)
        password = String(required=True)
        confirm_password = String(required=True)

    success = Boolean()

    def mutate(self, info, uid, token, password, confirm_password):
        try:
            if not compare_digest(password, confirm_password):
                raise BadRequest(_("passwords do not match"))

            user = User.objects.get(pk=urlsafe_base64_decode(uid).decode())

            password_reset_token = PasswordResetTokenGenerator()

            if not password_reset_token.check_token(user, token):
                raise BadRequest(_("token is invalid!"))

            user.set_password(password)

            user.save()

            return ConfirmResetPassword(success=True)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            raise BadRequest(_(f"something went wrong: {e!s}"))


class UploadAvatar(BaseMutation):
    class Arguments:
        avatar = Upload(required=True)

    user = Field(UserType)

    def mutate(self, info, avatar):
        if not info.context.user.is_authenticated:
            raise PermissionDenied(permission_denied_message)

        try:
            info.context.user.avatar = avatar
            info.context.user.save()
        except Exception as e:
            raise BadRequest(str(e))

        return UploadAvatar(user=info.context.user)
