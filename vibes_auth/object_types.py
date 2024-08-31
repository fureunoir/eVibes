import graphene
from graphene_django import DjangoObjectType

from core.object_types import ProductType
from vibes_auth.models import User


class UserType(DjangoObjectType):
    recently_viewed = graphene.Field(lambda: ProductType)

    class Meta:
        model = User
        fields = ["uuid", "email", "phone_number", "avatar", "is_verified", "is_active", "is_superuser", "last_login",
                  "is_staff", "last_login", "groups", "user_permissions", "date_joined", "first_name", "last_name",
                  "recently_viewed"]
