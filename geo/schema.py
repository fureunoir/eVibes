import graphene

from geo.models import Address
from geo.object_types import AddressType
from geo.utils import PointScalar


class CreateAddress(graphene.Mutation):
    class Arguments:
        location = PointScalar()

    address = graphene.Field(AddressType)

    def mutate(self, info, location):
        address = Address.objects.create(location=location)
        return CreateAddress(address=address)
