from django.urls import path, include
from rest_framework.routers import DefaultRouter

from geo.viewsets import AddressViewSet, CountryViewSet, StateViewSet, CityViewSet, PostalCodeViewSet

geo_router = DefaultRouter()
geo_router.register(r'addresses', AddressViewSet, basename='addresses')
geo_router.register(r'countries', CountryViewSet, basename='countries')
geo_router.register(r'states', StateViewSet, basename='states')
geo_router.register(r'cities', CityViewSet, basename='cities')
geo_router.register(r'postal_codes', PostalCodeViewSet, basename='postal_codes')

urlpatterns = [
    path(r'', include(geo_router.urls)),
]
