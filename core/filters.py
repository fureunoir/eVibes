import django_filters
from django.db.models import Q
from django.utils.translation import get_language
from django_filters import OrderingFilter, filters

from core.models import Product, Order, Category, AttributeValue


class CaseInsensitiveListFilter(filters.BaseInFilter, filters.CharFilter):
    def filter(self, qs, value):
        if value:
            lookup = f'{self.field_name}__icontains'
            q_objects = Q()
            for v in value:
                q_objects |= Q(**{lookup: v})
            qs = qs.filter(q_objects)
        return qs


class TranslatedCharFilter(django_filters.CharFilter):

    def filter(self, qs, value):
        if value:
            language_code = self.parent.request.LANGUAGE_CODE if self.parent.request else get_language()
            field_name = f'translations__{language_code}__{self.field_name}'
            return qs.filter(**{f'{field_name}__icontains': value})
        return qs


class ProductFilter(django_filters.FilterSet):
    uuid = django_filters.UUIDFilter(field_name='uuid', lookup_expr='exact', label='UUID')
    name = TranslatedCharFilter(field_name='name', label='Name')
    categories = TranslatedCharFilter(field_name='category__name', label="Categories")
    tags = TranslatedCharFilter(field_name="tags__name", label="Tags")
    min_price = django_filters.NumberFilter(field_name='stocks__price', lookup_expr='gte', label="Min Price")
    max_price = django_filters.NumberFilter(field_name='stocks__price', lookup_expr='lte', label="Max Price")
    is_active = django_filters.BooleanFilter(field_name='active', label='Is Active')
    brand = django_filters.CharFilter(field_name='brand__name', lookup_expr='icontains', label="Brand")
    attribute_values = django_filters.ModelMultipleChoiceFilter(
        field_name='attributes',
        queryset=AttributeValue.objects.all(),
        label='Attribute Values',
    )

    order_by = OrderingFilter(
        fields=(
            ('uuid', 'uuid'),
            ('translations__name', 'name'),
            ('created', 'created'),
            ('modified', 'modified'),
            ('stocks__price', 'price'),
            ('?', 'random')
        )
    )

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'categories', 'is_active', 'tags', 'min_price', 'max_price', 'attribute_values']


class OrderFilter(django_filters.FilterSet):
    uuid = django_filters.UUIDFilter(field_name='uuid', lookup_expr='exact')
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains', label="Status")

    order_by = OrderingFilter(
        fields=(
            ('uuid', 'uuid'),
            ('status', 'status'),
            ('created', 'created'),
            ('modified', 'modified'),
            ('buy_time', 'buy_time'),
            ('?', 'random')
        )
    )

    class Meta:
        model = Order
        fields = ['uuid', 'user_email', 'status']


class CategoryFilter(django_filters.FilterSet):
    uuid = django_filters.CharFilter(lookup_expr='exact')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['uuid', 'is_active', 'name', ]
        order_by = ['uuid', 'name', ]
