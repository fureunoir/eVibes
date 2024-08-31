from graphene_django import DjangoObjectType

from geo.models import Address
from geo.utils import PointScalar


class AddressType(DjangoObjectType):
    location = PointScalar()

    class Meta:
        model = Address
