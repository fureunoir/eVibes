import graphene
from django.contrib.auth.models import Group, Permission
from graphene import relay
from graphene_django import DjangoObjectType

from core.models import Order
from core.object_types import ProductType, OrderType
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
    avatar = graphene.String()

    class Meta:
        model = User
        fields = ["uuid", "email", "phone_number", "avatar", "is_verified", "is_active", "is_superuser", "last_login",
                  "is_staff", "last_login", "groups", "user_permissions", "date_joined", "first_name", "last_name",
                  "recently_viewed", "orders"]
        interfaces = (relay.Node,)
        filter_fields = ['email', 'is_active', 'uuid', 'first_name', 'last_name', 'is_superuser', 'is_staff',]

    def resolve_avatar(self, info) -> str:
        if self.avatar.file:
            return info.context.build_absolute_uri(self.avatar.url)
        else:
            return ''

    def resolve_orders(self, info):
        return Order.objects.filter(user=self) or []
