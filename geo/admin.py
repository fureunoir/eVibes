import swapper
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from core.admin import BasicModelAdmin

from .models import (
    Address,
    AlternativeName,
    City,
    Continent,
    Country,
    District,
    PostalCode,
    Region,
    Subregion,
)


class CitiesAdmin(admin.ModelAdmin):
    raw_id_fields = ["alt_names"]


class ContinentAdmin(CitiesAdmin):
    list_display = ["name", "code"]


class CountryAdmin(CitiesAdmin):
    list_display = [
        "name",
        "code",
        "code3",
        "tld",
        "phone",
        "continent",
        "area",
        "population",
    ]
    search_fields = ["name", "code", "code3", "tld", "phone"]
    filter_horizontal = ["neighbours"]


class RegionAdmin(CitiesAdmin):
    ordering = ["name_std"]
    list_display = ["name_std", "code", "country"]
    search_fields = ["name", "name_std", "code"]


class SubregionAdmin(CitiesAdmin):
    ordering = ["name_std"]
    list_display = ["name_std", "code", "region"]
    search_fields = ["name", "name_std", "code"]
    raw_id_fields = ["alt_names", "region"]


class CityAdmin(CitiesAdmin):
    ordering = ["name_std"]
    list_display = ["name_std", "subregion", "region", "country", "population"]
    search_fields = ["name", "name_std"]
    raw_id_fields = ["alt_names", "region", "subregion"]


class DistrictAdmin(CitiesAdmin):
    raw_id_fields = ["alt_names", "city"]
    list_display = ["name_std", "city"]
    search_fields = ["name", "name_std"]


class AltNameAdmin(admin.ModelAdmin):
    ordering = ["name"]
    list_display = ["name", "language_code", "is_preferred", "is_short", "is_historic"]
    list_filter = ["is_preferred", "is_short", "is_historic", "language_code"]
    search_fields = ["name"]


class PostalCodeAdmin(CitiesAdmin):
    ordering = ["code"]
    list_display = ["code", "subregion_name", "region_name", "country"]
    search_fields = [
        "code",
        "country__name",
        "region_name",
        "subregion_name",
        "region__name",
    ]


@admin.register(Address)
class AddressAdmin(BasicModelAdmin, GISModelAdmin):
    list_display = ("street", "city", "region", "postal_code", "country", "user")
    search_fields = (
        "street",
        "city__name",
        "postal_code__name",
        "country__name",
        "user__email",
    )
    list_filter = ("city", "region", "country")
    ordering = ("country", "city", "street")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("country", "city", "region", "postal_code", "user")


if not swapper.is_swapped("geo", "Continent"):
    admin.site.register(Continent, ContinentAdmin)
if not swapper.is_swapped("geo", "Country"):
    admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Subregion, SubregionAdmin)
if not swapper.is_swapped("geo", "City"):
    admin.site.register(City, CityAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(AlternativeName, AltNameAdmin)
admin.site.register(PostalCode, PostalCodeAdmin)
