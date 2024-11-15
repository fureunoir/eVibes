from hmac import compare_digest
from uuid import uuid4

import graphene
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import PermissionDenied, BadRequest
from django.http import Http404
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import ValidationError

from core.abstract import BaseMutation
from vibes_auth.models import User
from vibes_auth.object_types import UserType
from vibes_auth.serializers import TokenVerifySerializer, TokenRefreshSerializer, TokenObtainPairSerializer
from vibes_auth.utils.email import send_verification_email_task, send_reset_password_email_task
from vibes_auth.validators import is_valid_phone_number, is_valid_email


class CreateUser(BaseMutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        last_name = graphene.String()
        first_name = graphene.String()
        phone_number = graphene.String()
        is_subscribed = graphene.Boolean()
        language = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, email, password, confirm_password, last_name=None, first_name=None, phone_number=None,
               is_subscribed=None, language=None):
        try:
            if compare_digest(password, confirm_password):
                user = User.objects.create_user(email=email, password=password, last_name=last_name,
                                                first_name=first_name, phone_number=phone_number,
                                                is_subscribed=is_subscribed if is_subscribed is not None else False,
                                                language=language if language is not None else 'en-GB')
                return CreateUser(user=user)
            else:
                raise BadRequest("Passwords do not match.")
        except Exception as e:
            raise BadRequest(str(e))


class UpdateUser(BaseMutation):
    class Arguments:
        uuid = graphene.UUID(required=True)
        email = graphene.String()
        phone_number = graphene.String()
        password = graphene.String()
        confirm_password = graphene.String()
        is_verified = graphene.Boolean()
        first_name = graphene.String()
        last_name = graphene.String()
        language = graphene.String()
        is_active = graphene.Boolean()
        is_staff = graphene.Boolean()
        user_permissions = graphene.List(graphene.String)
        groups = graphene.List(graphene.String)

    user = graphene.Field(UserType)

    def mutate(self, info, uuid, **kwargs):

        try:

            user = User.objects.get(uuid=uuid)

        except User.DoesNotExist:

            raise Http404(f"User with the given uuid: {uuid} does not exist.")

        if info.context.user is not user and info.context.user.is_staff and not info.context.user.has_perm(
                'vibes_auth.change_user') and not info.context.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action")

        email = kwargs.get('email', None)

        if email is not None and not is_valid_email(email):
            raise BadRequest("Malformed email address.")

        if email != user.email and email is not None:
            user.is_active = False
            user.is_verified = False
            user.activation_token = uuid4()
            send_verification_email_task.delay(user.pk)
            user.email = email


        phone_number = kwargs.get('phone_number', None)

        if phone_number is not None and is_valid_phone_number(phone_number) and (
                (info.context.user == user) or info.context.user.is_superuser):
            user.phone_number = phone_number

        password = kwargs.get('password', '')
        confirm_password = kwargs.get('confirm_password', '')

        if (((not compare_digest(password, '') and confirm_password is not None) and compare_digest(password,
                                                                                                    confirm_password)) and (
                (info.context.user == user) or info.context.user.is_superuser)):
            user.set_password(password)

        for attr, value in kwargs.items():
            if attr not in ['groups', 'user_permissions', 'password', 'confirm_password', 'email', 'phone_number',
                            'is_verified', 'is_staff', 'is_active']:
                setattr(user, attr, value)

        user.save()

        return UpdateUser(user=user)


class DeleteUser(BaseMutation):
    class Arguments:
        email = graphene.String()
        uuid = graphene.UUID()

    success = graphene.Boolean()

    def mutate(self, info, uuid=None, email=None):
        if info.context.user.is_superuser or info.context.user.has_perm('vibes_auth.delete_user'):
            try:
                if uuid is not None:
                    User.objects.get(uuid=uuid).delete()
                elif email is not None:
                    User.objects.get(email=email).delete()
                else:
                    raise BadRequest(f"uuid or email must be specified")
                return DeleteUser(success=True)
            except User.DoesNotExist:
                raise Http404(f"User with the given uuid: {uuid} or email: {email} does not exist.")
        raise PermissionDenied("You do not have permission to perform this action: 'vibes_auth.delete_user'")


class ObtainJSONWebToken(BaseMutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    refresh_token = graphene.String()
    access_token = graphene.String()

    def mutate(self, info, email, password):
        serializer = TokenObtainPairSerializer(data={'email': email, 'password': password})
        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(email=email)
            return ObtainJSONWebToken(
                user=user,
                refresh_token=serializer.validated_data['refresh'],
                access_token=serializer.validated_data['access'],
            )
        except Exception as e:
            raise PermissionDenied(f"Invalid credentials provided: {str(e)}")


class RefreshJSONWebToken(BaseMutation):
    class Arguments:
        refresh_token = graphene.String(required=True)

    access_token = graphene.String()
    user = graphene.Field(UserType)
    refresh_token = graphene.String()

    def mutate(self, info, refresh_token):
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
            return RefreshJSONWebToken(
                access_token=serializer.validated_data['access'],
                refresh_token=serializer.validated_data['refresh'],
                user=User.objects.get(uuid=serializer.validated_data['user']['uuid'])
            )
        except Exception as e:
            raise PermissionDenied(f"Invalid refresh token provided: {str(e)}")


class VerifyJSONWebToken(BaseMutation):
    class Arguments:
        token = graphene.String(required=True)

    token_is_valid = graphene.Boolean()
    user = graphene.Field(UserType)

    def mutate(self, info, token):
        serializer = TokenVerifySerializer(data={'token': token})
        try:
            serializer.is_valid(raise_exception=True)
            user_uuid = serializer.validated_data['user']['uuid']
            user = User.objects.get(pk=user_uuid)
            return VerifyJSONWebToken(
                token_is_valid=True,
                user=user,
            )
        except ValidationError:
            return VerifyJSONWebToken(token_is_valid=False, user=None)


class ActivateUser(BaseMutation):
    class Arguments:
        uid = graphene.String(required=True)
        token = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, uid, token):
        try:
            token = urlsafe_base64_decode(token).decode()
            uuid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uuid)

            if not user.check_token(token):
                raise BadRequest("Activation link is invalid!")

            if user.is_active:
                raise BadRequest("Account already activated!")

            user.is_active = True
            user.is_verified = True
            user.save()

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            raise BadRequest(f"Something went wrong: {str(e)}")

        return ActivateUser(success=True)


class ResetPassword(BaseMutation):
    class Arguments:
        email = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        send_reset_password_email_task.delay(user_pk=user.uuid)

        return ResetPassword(success=True)


class ConfirmResetPassword(BaseMutation):
    class Arguments:
        uid = graphene.String(required=True)
        token = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, uid, token, password, confirm_password):
        try:

            if not compare_digest(password, confirm_password):
                raise BadRequest('Passwords do not match')

            user = User.objects.get(pk=urlsafe_base64_decode(uid).decode())

            password_reset_token = PasswordResetTokenGenerator()

            if not password_reset_token.check_token(user, token):
                raise BadRequest('Token is invalid!')

            user.set_password(password)

            user.save()

            return ConfirmResetPassword(success=True)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            raise BadRequest(f'Something went wrong: {str(e)}')
