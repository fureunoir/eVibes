from graphene import relay
from graphene_django import DjangoObjectType

from geo.models import Address
from geo.utils import PointScalar


class AddressType(DjangoObjectType):
    location = PointScalar()

    class Meta:
        model = Address
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['city', 'country']
