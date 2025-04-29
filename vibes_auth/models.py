from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as BaseGroup
from django.db.models import (
    BooleanField,
    CharField,
    EmailField,
    ImageField,
    JSONField,
    ManyToManyField,
    UUIDField,
)
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken as BaseBlacklistedToken,
)
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken as BaseOutstandingToken,
)

from core.abstract import NiceModel
from evibes.settings import LANGUAGE_CODE, LANGUAGES
from vibes_auth.managers import UserManager
from vibes_auth.validators import validate_phone_number


class User(AbstractUser, NiceModel):
    def get_uuid_as_path(self, *args):
        return str(self.uuid) + "/" + args[0]

    email = EmailField(_("email"), unique=True, help_text=_("user email address"))
    phone_number = CharField(
        _("phone_number"),
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text=_("user phone number"),
        validators=[
            validate_phone_number,
        ],
    )
    username = None
    first_name = CharField(_("first_name"), max_length=150, blank=True, null=True)  # noqa: DJ001
    last_name = CharField(_("last_name"), max_length=150, blank=True, null=True)  # noqa: DJ001
    avatar = ImageField(
        null=True,
        verbose_name=_("avatar"),
        upload_to=get_uuid_as_path,
        blank=True,
        help_text=_("user profile image"),
    )

    is_verified = BooleanField(
        default=False,
        verbose_name=_("is verified"),
        help_text=_("user verification status"),
    )
    is_active = BooleanField(
        _("is_active"),
        default=False,
        help_text=_("unselect this instead of deleting accounts"),
    )
    is_subscribed = BooleanField(
        verbose_name=_("is_subscribed"), help_text=_("user's newsletter subscription status"), default=False
    )
    recently_viewed = ManyToManyField(
        "core.Product",
        verbose_name=_("recently viwed"),
        blank=True,
        help_text=_("recently viewed products"),
    )

    activation_token = UUIDField(default=uuid4, verbose_name=_("activation token"))
    language = CharField(choices=LANGUAGES, default=LANGUAGE_CODE, null=False, blank=False, max_length=7)
    attributes = JSONField(verbose_name=_("attributes"), default=dict, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def add_to_recently_viewed(self, product_uuid):
        if not self.recently_viewed.filter(uuid=product_uuid).exists():
            if not self.recently_viewed.count() >= 48:
                self.recently_viewed.add(product_uuid)
            else:
                self.recently_viewed.remove(self.recently_viewed.first())
                self.recently_viewed.add(product_uuid)

    def check_token(self, token):
        return str(token) == str(self.activation_token)

    def __str__(self):
        return self.email

    class Meta:
        swappable = "AUTH_USER_MODEL"
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Group(BaseGroup):
    class Meta:
        proxy = True
        verbose_name = _("group")
        verbose_name_plural = _("groups")


class OutstandingToken(BaseOutstandingToken):
    class Meta:
        proxy = True
        verbose_name = _("outstanding token")
        verbose_name_plural = _("outstanding tokens")


class BlacklistedToken(BaseBlacklistedToken):
    class Meta:
        proxy = True
        verbose_name = _("blacklisted token")
        verbose_name_plural = _("blacklisted tokens")
