from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as BaseGroup
from django.db.models import EmailField, CharField, ImageField, BooleanField, ManyToManyField, UUIDField
from django.utils.translation import gettext_lazy as _

from core.abstract import NiceModel
from evibes.settings import LANGUAGES
from vibes_auth.managers import UserManager
from vibes_auth.validators import validate_phone_number


class User(AbstractUser, NiceModel):
    def get_uuid_as_path(self, *args):
        return str(self.uuid) + '/' + args[0]

    email = EmailField(_('email'), unique=True, help_text=_("user's email address"))
    phone_number = CharField(_('phone number'), max_length=20, unique=True, blank=True, null=True,
                             help_text=_("user's phone number"), validators=[validate_phone_number, ])
    username = None
    first_name = CharField(_("first name"), max_length=150, blank=True, null=True)
    last_name = CharField(_("last name"), max_length=150, blank=True, null=True)
    avatar = ImageField(null=True, verbose_name=_('avatar'), upload_to=get_uuid_as_path, blank=True,
                        help_text=_("user's profile image"))

    is_verified = BooleanField(default=False, verbose_name=_('is verified'), help_text=_("user's verification status"))
    is_active = BooleanField(
        _("is active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_subscribed = BooleanField(verbose_name=_('is subscibed'),
                                 help_text=_("user's newsletter subscription status"),
                                 default=False)
    recently_viewed = ManyToManyField('core.Product', verbose_name=_('recently viewed'), blank=True,
                                      help_text=_("user's recently viewed products"))

    activation_token = UUIDField(default=uuid4, verbose_name=_('activation token'))
    language = CharField(choices=LANGUAGES, default='en-GB', null=False, blank=False, max_length=7)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def add_to_recently_viewed(self, product_uuid):
        if not self.recently_viewed.filter(uuid=product_uuid).exists():
            if not self.recently_viewed.count() >= 48:
                self.recently_viewed.add(product_uuid)

    def check_token(self, token):
        if str(token) == str(self.activation_token):
            return True
        return False

    def __str__(self):
        return self.email

    class Meta:
        swappable = "AUTH_USER_MODEL"
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Group(BaseGroup):
    pass

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
