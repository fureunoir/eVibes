import graphene
from django.contrib.auth.models import Group, Permission
from graphene import relay
from graphene_django import DjangoObjectType

from core.models import Order
from core.object_types import ProductType, OrderType, WishlistType
from payments.object_types import BalanceType
from vibes_auth.models import User


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
        interfaces = (relay.Node,)
        filter_fields = ['name', 'id']


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]
        interfaces = (relay.Node,)
        filter_fields = ['name', 'id']


class UserType(DjangoObjectType):
    recently_viewed = graphene.Field(lambda: ProductType)
    groups = graphene.List(lambda: GroupType)
    user_permissions = graphene.List(lambda: PermissionType)
    orders = graphene.List(lambda: OrderType)
    wishlist = graphene.Field(lambda: WishlistType)
    balance = graphene.Field(lambda: BalanceType, source='payments_balance')
    avatar = graphene.String()

    class Meta:
        model = User
        fields = ["uuid", "email", "phone_number", "avatar", "is_verified", "is_active", "is_superuser", "last_login",
                  "is_staff", "last_login", "is_subscribed", "groups", "user_permissions", "date_joined", "first_name",
                  "last_name", "recently_viewed", "orders", "wishlist", "payments_balance"]
        interfaces = (relay.Node,)
        filter_fields = ['email', 'is_active', 'uuid', 'first_name', 'last_name', 'is_superuser', 'is_staff', ]

    def resolve_wishlist(self, info):
        return self.user_related_wishlist

    def resolve_balance(self, info):
        return self.payments_balance

    def resolve_avatar(self, info) -> str:
        if self.avatar:
            return info.context.build_absolute_uri(self.avatar.url)
        else:
            return ''

    def resolve_orders(self, info):
        return self.orders.all() if self.orders.count() >= 1 else []

    def resolve_recently_viewed(self, info):
        return self.recently_viewed.all() if self.recently_viewed.count() >= 1 else []

    def resolve_groups(self, info):
        return self.groups.all() if self.groups.count() >= 1 else []

    def resolve_user_permissions(self, info):
        return self.user_permissions.all() if self.user_permissions.count() >= 1 else []
