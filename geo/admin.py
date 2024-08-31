from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin  # Use GeoModelAdmin for geospatial models

from .models import WorldBorder, Address


@admin.register(WorldBorder)
class WorldBorderAdmin(GISModelAdmin):
    list_display = ('name', 'iso2', 'iso3', 'un', 'area', 'pop2005', 'region', 'subregion')
    search_fields = ('name', 'iso2', 'iso3', 'fips')
    list_filter = ('region', 'subregion')
    ordering = ('name',)


@admin.register(Address)
class AddressAdmin(GISModelAdmin):
    list_display = ('street_address', 'city', 'state', 'postal_code', 'country', 'user')
    search_fields = ('street_address', 'city', 'postal_code', 'country', 'user__email')
    list_filter = ('city', 'state', 'country')
    ordering = ('country', 'city', 'street_address')
