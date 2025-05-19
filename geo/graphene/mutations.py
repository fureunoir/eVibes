import graphene
from django.core.exceptions import BadRequest
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from graphene.types.generic import GenericScalar
from rest_framework.exceptions import PermissionDenied

from core.graphene import BaseMutation
from core.utils.messages import permission_denied_message
from geo.graphene.object_types import AddressType
from geo.models import Address
from geo.utils.nominatim import fetch_address_suggestions


class CreateAddress(graphene.Mutation):
    class Arguments:
        raw_data = graphene.String(
            required=True,
            description=_("original address string provided by the user")
        )

    address = graphene.Field(AddressType)

    @staticmethod
    def mutate(_parent, info, raw_data):
        user = info.context.user if info.context.user.is_authenticated else None

        address = Address.objects.create(
            raw_data=raw_data,
            user=user
        )
        return CreateAddress(address=address)


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


class AutocompleteAddress(BaseMutation):
    class Arguments:
        q = graphene.String()
        limit = graphene.Int()

    suggestions = GenericScalar()

    @staticmethod
    def mutate(_parent, info, q, limit):
        if 1 > limit > 10:
            raise BadRequest(_("limit must be between 1 and 10"))
        try:
            suggestions = fetch_address_suggestions(query=q, limit=limit)
        except Exception as e:
            raise BadRequest(f"geocoding error: {e!s}") from e

        return AutocompleteAddress(suggestions=suggestions)
