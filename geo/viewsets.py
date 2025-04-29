from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from core.permissions import IsOwner
from geo.models import Address, City, Region
from geo.serializers import AddressSerializer, CitySerializer, CountrySerializer, PostalCodeSerializer, RegionSerializer


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsOwner, IsAdminUser]


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Address.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]


class PostalCodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Address.objects.all()
    serializer_class = PostalCodeSerializer
    permission_classes = [AllowAny]
