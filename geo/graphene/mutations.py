import graphene
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied

from core.graphene import BaseMutation
from core.utils.messages import permission_denied_message
from geo.graphene.object_types import AddressType
from geo.models import Address, City, PostalCode
from geo.utils import PointScalar


class CreateAddress(BaseMutation):
    class Arguments:
        location = PointScalar()
        street = graphene.String()
        city_uuid = graphene.UUID()
        postal_code_uuid = graphene.UUID()

    address = graphene.Field(AddressType)

    @staticmethod
    def mutate(_parent, info, street, city_uuid, postal_code_uuid):
        if info.context.user.is_authenticated:
            try:
                city = City.objects.get(uuid=city_uuid)
                postal_code = PostalCode.objects.get(uuid=postal_code_uuid)
            except City.DoesNotExist:
                name = "City"
                raise Http404(_(f"{name} does not exist: {city_uuid}"))
            except PostalCode.DoesNotExist:
                name = "PostalCode"
                raise Http404(_(f"{name} does not exist: {postal_code_uuid}"))

            address = Address.objects.create(
                street=street,
                city=city,
                postal_code=postal_code,
                region=city.region,
                country=city.country,
                user=info.context.user,
            )

            return CreateAddress(address=address)

        else:
            raise PermissionDenied(permission_denied_message)


class UpdateAddress(BaseMutation):
    class Arguments:
        uuid = graphene.UUID(required=True)
        location = PointScalar()
        street = graphene.String()
        city_uuid = graphene.UUID()
        postal_code_uuid = graphene.UUID()

    address = graphene.Field(AddressType)

    @staticmethod
    def mutate(_parent, info, uuid, location=None, street=None, city_uuid=None, postal_code_uuid=None):
        try:
            address = Address.objects.get(uuid=uuid)

            if (
                info.context.user.is_superuser
                or info.context.user.has_perm("geo.change_address")
                or info.context.user == address.user
            ):
                address = Address.objects.get(uuid=uuid)

                if location is not None:
                    address.location = location

                if street is not None:
                    address.street = street

                if city_uuid is not None:
                    address.city = City.objects.get(uuid=city_uuid)

                if postal_code_uuid is not None:
                    address.postal_code = PostalCode.objects.get(uuid=postal_code_uuid)

                address.save()

                return UpdateAddress(address=address)

            raise PermissionDenied(permission_denied_message)

        except Address.DoesNotExist:
            name = "Address"
            raise Http404(_(f"{name} does not exist: {uuid}"))


class DeleteAddress(BaseMutation):
    class Arguments:
        uuid = graphene.UUID(required=True)

    success = graphene.Boolean()

    @staticmethod
    def mutate(_parent, info, uuid):
        try:
            address = Address.objects.get(uuid=uuid)
            if (
                info.context.user.is_superuser
                or info.context.user.has_perm("geo.delete_address")
                or info.context.user == address.user
            ):
                address.delete()
                return DeleteAddress(success=True)

            raise PermissionDenied(permission_denied_message)

        except Address.DoesNotExist:
            name = "Address"
            raise Http404(_(f"{name} does not exist: {uuid}"))
