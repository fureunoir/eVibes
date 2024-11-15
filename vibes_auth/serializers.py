from typing import Dict, Any, Optional, Type

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.fields import SerializerMethodField, CharField, EmailField, BooleanField
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import PasswordField, AuthUser
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken, Token

from core.serializers import ProductSerializer
from evibes.settings import logger
from vibes_auth.models import User
from vibes_auth.utils.email import send_verification_email_task
from core.utils.security import is_safe_key
from evibes import settings
from constance import config


class UserSerializer(ModelSerializer):
    avatar_url = SerializerMethodField(required=False, read_only=True)
    password = CharField(write_only=True, required=False)
    is_staff = BooleanField(read_only=True)

    @staticmethod
    def get_avatar_url(obj) -> str:
        if obj.avatar:
            return f'https://api.{config.BASE_DOMAIN}/{settings.MEDIA_URL}{str(obj.avatar)}'
        return f'https://api.{config.BASE_DOMAIN}/{settings.STATIC_URL}person.png'

    class Meta:
        model = User
        fields = ['uuid', 'email', 'avatar_url', 'is_staff', 'created', 'first_name', 'last_name',
                  'password', 'phone_number', 'is_subscribed', 'modified',
                  'created']

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data.pop('password'))
        for key, attr in validated_data.items():
            if is_safe_key(key):
                setattr(user, key, attr)
        user.save()
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            if attr == 'password':
                instance.set_password(value)
            if attr == 'email':
                if value != instance.email:
                    send_verification_email_task.delay(instance.pk)
                    setattr(instance, attr, value)

        instance.save()
        return instance

    def validate(self, attr):
        if 'password' in attr:
            validate_password(attr['password'])
        return attr


class TokenObtainSerializer(Serializer):
    username_field = User.USERNAME_FIELD
    token_class: Optional[Type[Token]] = None

    default_error_messages = {
        "no_active_account": _("No active account found with the given credentials")
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.user = None
        self.fields[self.username_field] = CharField(write_only=True)
        self.fields["password"] = PasswordField()

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}

    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        return cls.token_class.for_user(user)  # type: ignore


class TokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        logger.debug("Data validated")

        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["user"] = UserSerializer(self.user).data

        logger.debug("Data formed")

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
            logger.debug("Updated last login")

        logger.debug("Returning data")
        return data


class TokenRefreshSerializer(Serializer):
    refresh = CharField()
    access = CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)
            user = User.objects.get(uuid=refresh.payload['user_uuid'])
            data["user"] = UserSerializer(user).data

        return data


class TokenVerifySerializer(Serializer):
    token = CharField(write_only=True)

    def validate(self, attrs: Dict[str, None]) -> Dict[Any, Any]:
        token = UntypedToken(attrs["token"])

        if (
                api_settings.BLACKLIST_AFTER_ROTATION
                and "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS
        ):
            jti = token.get(api_settings.JTI_CLAIM)
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise ValidationError(_("token is blacklisted"))

        try:
            payload = UntypedToken(attrs['token']).payload
        except TokenError:
            raise ValidationError(_("invalid token"))

        try:
            user_uuid = payload['user_uuid']
            user = User.objects.get(uuid=user_uuid)
        except KeyError:
            raise ValidationError(_("no user_uuid claim present in token"))
        except User.DoesNotExist:
            raise ValidationError(_("user does not exist"))

        attrs['user'] = UserSerializer(user).data
        return attrs


class ConfirmPasswordResetSerializer(Serializer):
    uidb64 = CharField(write_only=True, required=True)
    token = CharField(write_only=True, required=True)
    password = CharField(write_only=True, required=True)
    confirm_password = CharField(write_only=True, required=True)


class ResetPasswordSerializer(Serializer):
    email = EmailField(write_only=True, required=True)


class ActivateEmailSerializer(Serializer):
    uidb64 = CharField(required=True)
    token = CharField(required=True)
