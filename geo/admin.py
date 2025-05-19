from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Address


@admin.register(Address)
class AddressAdmin(GISModelAdmin):
    list_display = ("street", "city", "region", "country", "user")
    list_filter = ("country", "region")
    search_fields = ("raw_data", "street", "city", "postal_code", "user__email")

    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 37.61556,
            "default_lat": 55.75222,
            "default_zoom": 6,
        }
    }
