import graphene
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from geo.models import Address
from geo.object_types import AddressType
from geo.utils import PointScalar


class CreateAddress(graphene.Mutation):
    class Arguments:
        location = PointScalar()
        street_address = graphene.String()
        city = graphene.String()
        postal_code = graphene.String()
        locality = graphene.String()
        state = graphene.String()
        country = graphene.String()

    address = graphene.Field(AddressType)

    def mutate(self, info, location, street_address, city, postal_code, locality, state, country):
        if info.context.user.is_anonymous:
            address = Address.objects.create(location=location,
                                             street_address=street_address,
                                             city=city,
                                             postal_code=postal_code,
                                             locality=locality,
                                             state=state,
                                             country=country,
                                             user=info.context.user)
            return CreateAddress(address=address)
        else:
            raise NotAuthenticated("You must be authenticated to perform this action.")


class UpdateAddress(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)
        location = PointScalar()
        street_address = graphene.String()
        city = graphene.String()
        postal_code = graphene.String()
        locality = graphene.String()
        state = graphene.String()
        country = graphene.String()

    address = graphene.Field(AddressType)

    def mutate(self, info, uuid, location=None, street_address=None, city=None, postal_code=None, locality=None, state=None, country=None):
        if info.context.user.is_superuser or info.context.user.has_perm(
                'geo.delete_address') or info.context.user is Address.objects.get(uuid=uuid).user:
            address = Address.objects.get(uuid=uuid)
            return UpdateAddress(address=address)
        else:
            raise PermissionDenied("You do not have permissions to perform this action.")


class DeleteAddress(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, uuid, location):
        if info.context.user.is_superuser or info.context.user.has_perm(
                'geo.delete_address') or info.context.user is Address.objects.get(uuid=uuid).user:
            Address.objects.get(uuid=uuid).delete()
            return DeleteAddress(success=True)
        else:
            raise PermissionDenied("You do not have permissions to perform this action.")
