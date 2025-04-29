import django_filters

from vibes_auth.models import User


class UserFilter(django_filters.FilterSet):
    uuid = django_filters.CharFilter(lookup_expr="exact")
    email = django_filters.CharFilter(lookup_expr="iexact")
    is_staff = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()
    is_superuser = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ["uuid", "email", "is_active", "is_staff", "is_superuser"]
        order_by = [
            "uuid",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "created",
            "modified",
        ]
