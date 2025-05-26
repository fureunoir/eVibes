from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from graphene import Field, List, String, relay
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType
from graphql_relay.connection.array_connection import connection_from_array

from core.graphene.object_types import OrderType, ProductType, WishlistType
from core.models import Product
from evibes.settings import LANGUAGE_CODE, LANGUAGES
from payments.graphene.object_types import BalanceType
from vibes_auth.models import User


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
        interfaces = (relay.Node,)
        filter_fields = ["name", "id"]


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]
        interfaces = (relay.Node,)
        filter_fields = ["name", "id"]


class RecentProductConnection(relay.Connection):
    class Meta:
        node = ProductType


class UserType(DjangoObjectType):
    recently_viewed = relay.ConnectionField(
        RecentProductConnection,
        description=_("the products this user has viewed most recently (max 48), in reverse‐chronological order"),
    )
    groups = List(lambda: GroupType, description=_("groups"))
    user_permissions = List(lambda: PermissionType, description=_("permissions"))
    orders = List(lambda: OrderType, description=_("orders"))
    wishlist = Field(lambda: WishlistType, description=_("wishlist"))
    balance = Field(lambda: BalanceType, source="payments_balance", description=_("balance"))
    avatar = String(description=_("avatar"))
    attributes = GenericScalar(description=_("attributes may be used to store custom data"))
    language = String(description=_(f"language is one of the {LANGUAGES} with default {LANGUAGE_CODE}"))

    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "phone_number",
            "avatar",
            "is_verified",
            "is_active",
            "is_superuser",
            "last_login",
            "is_staff",
            "last_login",
            "is_subscribed",
            "groups",
            "user_permissions",
            "date_joined",
            "first_name",
            "last_name",
            "language",
            "recently_viewed",
            "orders",
            "attributes",
            "wishlist",
            "balance",
        ]
        interfaces = (relay.Node,)
        filter_fields = [
            "email",
            "is_active",
            "uuid",
            "first_name",
            "last_name",
            "is_superuser",
            "is_staff",
        ]

    def resolve_wishlist(self, info):
        return self.user_related_wishlist

    def resolve_balance(self, info):
        return self.payments_balance

    def resolve_avatar(self, info) -> str:
        if self.avatar:
            return info.context.build_absolute_uri(self.avatar.url)
        else:
            return ""

    def resolve_orders(self, info):
        return self.orders.all() if self.orders.count() >= 1 else []

    def resolve_recently_viewed(self, info, **kwargs):
        uuid_list = self.recently_viewed or []

        if not uuid_list:
            return connection_from_array([], kwargs)

        qs = Product.objects.filter(uuid__in=uuid_list)

        products_by_uuid = {str(p.uuid): p for p in qs}

        ordered_products = [products_by_uuid[u] for u in uuid_list if u in products_by_uuid]

        return connection_from_array(ordered_products, kwargs)

    def resolve_groups(self, info):
        return self.groups.all() if self.groups.count() >= 1 else []

    def resolve_user_permissions(self, info):
        return self.user_permissions.all() if self.user_permissions.count() >= 1 else []
