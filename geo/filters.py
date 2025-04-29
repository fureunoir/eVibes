import django_filters
from django_filters import OrderingFilter

from geo.models import City, Country, PostalCode, Region


class CountryFilter(django_filters.FilterSet):
    uuid = django_filters.CharFilter(lookup_expr="exact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    code = django_filters.CharFilter(lookup_expr="iexact")

    order_by = OrderingFilter(fields=(("uuid", "uuid"), ("name", "name"), ("?", "random")))

    class Meta:
        model = Country
        fields = ["uuid", "name", "code"]


class RegionFilter(django_filters.FilterSet):
    uuid = django_filters.CharFilter(lookup_expr="exact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    country_name = django_filters.CharFilter(lookup_expr="exact", field_name="country__name")
    country_code = django_filters.CharFilter(lookup_expr="exact", field_name="country__code")

    order_by = OrderingFilter(fields=(("uuid", "uuid"), ("name", "name"), ("?", "random")))

    class Meta:
        model = Region
        fields = ["uuid", "name", "country_name", "country_code"]


class CityFilter(django_filters.FilterSet):
    uuid = django_filters.CharFilter(lookup_expr="exact")
    name = django_filters.CharFilter(lookup_expr="icontains")
    region_name = django_filters.CharFilter(lookup_expr="exact", field_name="region__name")
    region_code = django_filters.CharFilter(lookup_expr="exact", field_name="region__code")

    order_by = OrderingFilter(fields=(("uuid", "uuid"), ("name", "name"), ("?", "random")))

    class Meta:
        model = City
        fields = ["uuid", "name", "region_name", "region_code"]


class PostalCodeFilter(django_filters.FilterSet):
    uuid = django_filters.CharFilter(lookup_expr="exact")
    code = django_filters.CharFilter(lookup_expr="icontains")
    city_name = django_filters.CharFilter(lookup_expr="iexact", field_name="city__name")
    region_name = django_filters.CharFilter(lookup_expr="iexact", field_name="region__name")
    country_name = django_filters.CharFilter(lookup_expr="iexact", field_name="country__name")

    class Meta:
        model = PostalCode
        fields = ["uuid", "code", "city_name", "region_name", "country_name"]
