import json
import logging

from django.db.models import Avg, FloatField, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.utils.http import urlsafe_base64_decode
from django_filters import BaseInFilter, BooleanFilter, CharFilter, FilterSet, NumberFilter, OrderingFilter, UUIDFilter

from core.models import Brand, Category, Feedback, Order, Product, Wishlist

logger = logging.getLogger(__name__)


class CaseInsensitiveListFilter(BaseInFilter, CharFilter):
    def filter(self, qs, value):
        if value:
            lookup = f"{self.field_name}__icontains"
            q_objects = Q()
            for v in value:
                q_objects |= Q(**{lookup: v})
            qs = qs.filter(q_objects)
        return qs


class ProductFilter(FilterSet):
    uuid = UUIDFilter(field_name="uuid", lookup_expr="exact", label="UUID")
    name = CharFilter(field_name="name", lookup_expr="icontains", label="Name")
    categories = CaseInsensitiveListFilter(field_name="category__name", label="Categories")
    category_uuid = CharFilter(field_name="category__uuid", lookup_expr="exact", label="Category")
    category_slugs = CaseInsensitiveListFilter(field_name="category__slug", label="Categories Slug")
    tags = CaseInsensitiveListFilter(field_name="tags__tag_name", label="Tags")
    min_price = NumberFilter(field_name="stocks__price", lookup_expr="gte", label="Min Price")
    max_price = NumberFilter(field_name="stocks__price", lookup_expr="lte", label="Max Price")
    is_active = BooleanFilter(field_name="is_active", label="Is Active")
    brand = CharFilter(field_name="brand__name", lookup_expr="iexact", label="Brand")
    attributes = CharFilter(method="filter_attributes", label="Attributes")
    quantity = NumberFilter(field_name="stocks__quantity", lookup_expr="gt", label="Quantity")
    slug = CharFilter(field_name="slug", lookup_expr="exact", label="Slug")
    is_digital = BooleanFilter(field_name="is_digital", label="Is Digital")

    order_by = OrderingFilter(
        fields=(
            ("uuid", "uuid"),
            ("rating", "rating"),
            ("name", "name"),
            ("slug", "slug"),
            ("created", "created"),
            ("modified", "modified"),
            ("stocks__price", "price"),
            ("?", "random"),
        ),
        initial="uuid",
    )

    class Meta:
        model = Product
        fields = [
            "uuid",
            "name",
            "categories",
            "category_uuid",
            "attributes",
            "created",
            "modified",
            "is_digital",
            "is_active",
            "tags",
            "slug",
            "min_price",
            "max_price",
            "brand",
            "quantity",
            "order_by",
        ]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        ordering_param = self.data.get("order_by", "")
        if ordering_param:
            order_fields = [field.strip("-") for field in ordering_param.split(",")]
            if "rating" in order_fields:
                feedback_qs = (
                    Feedback.objects.filter(order_product__product_id=OuterRef("pk"))
                    .values("order_product__product_id")
                    .annotate(avg_rating=Avg("rating"))
                    .values("avg_rating")
                )
                self.queryset = self.queryset.annotate(
                    rating=Coalesce(
                        Subquery(feedback_qs, output_field=FloatField()), Value(0, output_field=FloatField())
                    )
                )

    def filter_attributes(self, queryset, _name, value):
        if not value:
            return queryset

        if str(value).startswith("b64-"):
            value = urlsafe_base64_decode(value[4:]).decode()

        user = getattr(self.request, "user", None)
        can_view_inactive_attrvals = user and user.has_perm("view_attributevalue")

        pairs = [pair.strip() for pair in value.split(";") if "=" in pair]

        q_list = []
        for pair in pairs:
            attr_name, filter_part = pair.split("=", 1)
            attr_name = attr_name.strip()
            filter_part = filter_part.strip()

            if "-" in filter_part:
                method, raw_value = filter_part.split("-", 1)
            else:
                method = "iexact"
                raw_value = filter_part

            method = method.lower().strip()
            raw_value = self._infer_type(raw_value)

            base_filter = Q(**{"attributes__attribute__name__iexact": attr_name})
            if not can_view_inactive_attrvals:
                base_filter &= Q(**{"attributes__is_active": True})

            allowed_methods = {
                "iexact",
                "exact",
                "icontains",
                "contains",
                "isnull",
                "startswith",
                "istartswith",
                "endswith",
                "iendswith",
                "regex",
                "iregex",
                "lt",
                "lte",
                "gt",
                "gte",
                "in",
            }
            if method in allowed_methods:
                field_lookup = f"attributes__value__{method}"
            else:
                field_lookup = "attributes__value__icontains"

            base_filter &= Q(**{field_lookup: raw_value})
            q_list.append(base_filter)

        for q_obj in q_list:
            queryset = queryset.filter(q_obj)

        return queryset

    @staticmethod
    def _infer_type(value):
        try:
            parsed_value = json.loads(value)
            if isinstance(parsed_value, (list, dict)):
                return parsed_value
        except (json.JSONDecodeError, TypeError):
            pass

        if value.lower() in ["true", "false"]:
            return value.lower() == "true"

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        return value

    @property
    def qs(self):
        """
        Override the queryset property to annotate a “rating” field
        when the ordering parameters include “rating”. This makes ordering
        by rating possible.
        """
        qs = super().qs

        # Check if ordering by rating is requested (could be "rating" or "-rating")
        ordering_param = self.data.get("order_by", "")
        if ordering_param:
            order_fields = [field.strip() for field in ordering_param.split(",")]
            if any(field.lstrip("-") == "rating" for field in order_fields):
                # Annotate each product with its average rating.
                # Here we use a Subquery to calculate the average rating from the Feedback model.
                # Adjust the filter in Feedback.objects.filter(...) if your relationships differ.
                feedback_qs = (
                    Feedback.objects.filter(order_product__product_id=OuterRef("pk"))
                    .values("order_product__product_id")
                    .annotate(avg_rating=Avg("rating"))
                    .values("avg_rating")
                )
                qs = qs.annotate(
                    rating=Coalesce(
                        Subquery(feedback_qs, output_field=FloatField()), Value(0, output_field=FloatField())
                    )
                )
        return qs


class OrderFilter(FilterSet):
    uuid = UUIDFilter(field_name="uuid", lookup_expr="exact")
    user_email = CharFilter(field_name="user__email", lookup_expr="iexact")
    user = UUIDFilter(field_name="user__uuid", lookup_expr="exact")
    status = CharFilter(field_name="status", lookup_expr="icontains", label="Status")
    human_readable_id = CharFilter(field_name="human_readable_id", lookup_expr="exact")

    order_by = OrderingFilter(
        fields=(
            ("uuid", "uuid"),
            ("human_readable_id", "human_readable_id"),
            ("user_email", "user_email"),
            ("user", "user"),
            ("status", "status"),
            ("created", "created"),
            ("modified", "modified"),
            ("buy_time", "buy_time"),
            ("?", "random"),
        )
    )

    class Meta:
        model = Order
        fields = ["uuid", "human_readable_id", "user_email", "user", "status", "order_by"]


class WishlistFilter(FilterSet):
    uuid = UUIDFilter(field_name="uuid", lookup_expr="exact")
    user_email = CharFilter(field_name="user__email", lookup_expr="iexact")
    user = UUIDFilter(field_name="user__uuid", lookup_expr="exact")

    order_by = OrderingFilter(
        fields=(("uuid", "uuid"), ("created", "created"), ("modified", "modified"), ("?", "random"))
    )

    class Meta:
        model = Wishlist
        fields = ["uuid", "user_email", "user", "order_by"]


class CategoryFilter(FilterSet):
    uuid = UUIDFilter(field_name="uuid", lookup_expr="exact")
    name = CharFilter(field_name="name", lookup_expr="icontains")
    parent_uuid = UUIDFilter(field_name="parent__uuid", lookup_expr="exact")
    slug = CharFilter(field_name="slug", lookup_expr="exact")

    order_by = OrderingFilter(
        fields=(
            ("uuid", "uuid"),
            ("name", "name"),
            ("?", "random"),
        )
    )

    class Meta:
        model = Category
        fields = ["uuid", "name"]


class BrandFilter(FilterSet):
    uuid = UUIDFilter(field_name="uuid", lookup_expr="exact")
    name = CharFilter(field_name="name", lookup_expr="icontains")
    categories = CaseInsensitiveListFilter(field_name="categories__uuid", lookup_expr="exact")

    order_by = OrderingFilter(
        fields=(
            ("uuid", "uuid"),
            ("name", "name"),
            ("?", "random"),
        )
    )

    class Meta:
        model = Brand
        fields = ["uuid", "name"]


class FeedbackFilter(FilterSet):
    uuid = UUIDFilter(field_name="uuid", lookup_expr="exact")
    product = UUIDFilter(field_name="order_product__product__uuid", lookup_expr="exact")

    order_by = OrderingFilter(
        fields=(
            ("uuid", "uuid"),
            ("product", "product"),
            ("rating", "rating"),
            ("created", "created"),
            ("modified", "modified"),
            ("?", "random"),
        )
    )

    class Meta:
        model = Feedback
        fields = ["uuid", "product"]
