from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.permissions import IsOwner
from geo.docs.drf.viewsets import ADDRESS_SCHEMA
from geo.models import Address
from geo.serializers import AddressAutocompleteInputSerializer, AddressCreateSerializer, AddressSerializer
from geo.utils.nominatim import fetch_address_suggestions


@extend_schema_view(**ADDRESS_SCHEMA)
class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsOwner, IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return AddressCreateSerializer
        if self.action == 'autocomplete':
            return AddressAutocompleteInputSerializer
        return AddressSerializer

    @action(detail=False, methods=["get"], url_path="autocomplete")
    def autocomplete(self, request):
        serializer = AddressAutocompleteInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        q = serializer.validated_data["q"]
        limit = serializer.validated_data["limit"]

        try:
            suggestions = fetch_address_suggestions(query=q, limit=limit)
        except Exception as e:
            return Response(
                {"detail": _(f"Geocoding error: {e}")},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(suggestions, status=status.HTTP_200_OK)
