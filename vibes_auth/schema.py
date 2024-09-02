from hmac import compare_digest
from uuid import uuid4

import graphene
from django.contrib.auth.models import Permission, Group
from django.core.exceptions import PermissionDenied, BadRequest
from django.core.validators import validate_email
from django.http import Http404

from vibes_auth.models import User
from vibes_auth.object_types import UserType
from vibes_auth.serializers import TokenVerifySerializer, TokenRefreshSerializer, TokenObtainPairSerializer
from vibes_auth.utils.email import send_verification_email_task
from vibes_auth.validators import validate_phone_number


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        last_name = graphene.String()
        first_name = graphene.String()
        phone_number = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, email, password, confirm_password, last_name=None, first_name=None, phone_number=None):
        try:
            if compare_digest(password, confirm_password):
                user = User.objects.create_user(email=email, password=password, last_name=last_name,
                                                first_name=first_name, phone_number=phone_number)
                return CreateUser(user=user)
            else:
                raise BadRequest("Passwords do not match.")
        except Exception as e:
            raise BadRequest(str(e))


class UpdateUser(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)
        email = graphene.String()
        phone_number = graphene.String()
        password = graphene.String()
        confirm_password = graphene.String()
        is_verified = graphene.Boolean()
        is_active = graphene.Boolean()
        is_staff = graphene.Boolean()
        user_permissions = graphene.List(graphene.String)
        groups = graphene.List(graphene.String)

    user = graphene.Field(UserType)

    def mutate(self, info, uuid, email=None, phone_number=None, password=None, confirm_password=None, is_verified=None,
               is_active=None, is_staff=None,
               user_permissions=None, groups=None):

        try:

            user = User.objects.get(uuid=uuid)

        except User.DoesNotExist:

            raise Http404(f"User with the given uuid: {uuid} does not exist.")

        if info.context.user is not user and info.context.user.is_staff and not info.context.user.has_perm(
                'vibes_auth.change_user') and not info.context.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action")

        if (email is not None and validate_email(email)) and (email != user.email) and (
                (info.context.user == user) or info.context.user.is_superuser):
            user.is_active = False
            user.is_verified = False
            user.activation_token = uuid4()
            send_verification_email_task.delay(user.pk)
            user.email = email

        else:

            raise PermissionDenied("You do not have permission to perform this action")

        if phone_number is not None and validate_phone_number(phone_number) and (
                (info.context.user == user) or info.context.user.is_superuser):
            user.phone_number = phone_number

        if ((password is not None and confirm_password is not None) and compare_digest(password,
                                                                                       confirm_password)) and (
                (info.context.user == user) or info.context.user.is_superuser):
            user.set_password(password)

        if is_verified is not None and (info.context.user.is_superuser or info.context.user.is_staff):

            user.is_verified = is_verified

        else:

            raise PermissionDenied("You do not have permission to perform this action")

        if is_active is not None and (info.context.user.is_superuser or info.context.user.is_staff):

            user.is_active = is_active

        else:

            raise PermissionDenied("You do not have permission to perform this action")

        if user_permissions is not None and info.context.user.is_superuser:

            permissions_objs = Permission.objects.filter(codename__in=user_permissions)
            user.user_permissions.set(permissions_objs)

        else:

            raise PermissionDenied("You do not have permission to perform this action")

        if is_staff is not None and info.context.user.is_superuser:

            user.is_staff = is_staff

        else:

            raise PermissionDenied("You do not have permission to perform this action")

        if groups is not None and info.context.user.is_superuser:

            group_objs = Group.objects.filter(name__in=groups)
            user.groups.set(group_objs)

        else:

            raise PermissionDenied("You do not have permission to perform this action")

        user.save()

        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
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


class ObtainJSONWebToken(graphene.Mutation):
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
            raise PermissionDenied("Invalid credentials provided.")


class RefreshJSONWebToken(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required=True)

    access_token = graphene.String()

    def mutate(self, info, refresh_token):
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
            return RefreshJSONWebToken(
                access_token=serializer.validated_data['access'],
            )
        except Exception as e:
            raise PermissionDenied("Invalid refresh token provided.")


class VerifyJSONWebToken(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)

    token_is_valid = graphene.Boolean()
    user = graphene.Field(UserType)
    error = graphene.String()

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
        except Exception as e:
            return VerifyJSONWebToken(token_is_valid=False, user=None, error=str(e))
