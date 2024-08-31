import graphene
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from vibes_auth.models import User
from vibes_auth.object_types import UserType
from vibes_auth.serializers import TokenVerifySerializer, TokenRefreshSerializer, TokenObtainPairSerializer


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, email, password):
        user = User.objects.create_user(email=email, password=password)

        return CreateUser(user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String()
        phone_number = graphene.String()
        avatar = graphene.String()

    user = graphene.Field(UserType)

    @login_required
    def mutate(self, info, email=None, phone_number=None, avatar=None):
        user = info.context.user

        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        if avatar:
            user.avatar = avatar

        user.save()

        return UpdateUser(user=user)


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
            return VerifyJSONWebToken(token_is_valid=False, user=None)
