import django_filters
from core.models import Product, Order, User

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    active = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['name', 'category', 'active']
        order_by = ['name', 'created', 'modified']

class OrderFilter(django_filters.FilterSet):
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Order
        fields = ['user_email', 'status']
        order_by = ['user_email', 'status', 'created', 'modified']
