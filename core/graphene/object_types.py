from django.core.cache import cache
from django.db.models import Max, Min, QuerySet
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _
from graphene import UUID, Field, Float, Int, List, NonNull, ObjectType, String, relay
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.utils import camelize
from mptt.querysets import TreeQuerySet

from core.models import (
    Attribute,
    AttributeGroup,
    AttributeValue,
    Brand,
    Category,
    Feedback,
    Order,
    OrderProduct,
    Product,
    ProductImage,
    PromoCode,
    Promotion,
    Stock,
    Vendor,
    Wishlist,
)
from geo.graphene.object_types import AddressType

logger = __import__("logging").getLogger(__name__)


class AttributeType(DjangoObjectType):
    values = List(lambda: AttributeValueType, description=_("attribute values"))

    class Meta:
        model = Attribute
        interfaces = (relay.Node,)
        fields = ("uuid", "value_type", "name")
        filter_fields = ["uuid"]
        description = _("attributes")

    def resolve_values(self, info):
        base_qs = AttributeValue.objects.filter(attribute=self)
        product_uuid = getattr(info.context, "_product_uuid", None)

        if product_uuid:
            base_qs = base_qs.filter(product__uuid=product_uuid)

        return base_qs


class AttributeGroupType(DjangoObjectType):
    attributes = List(lambda: AttributeType, description=_("grouped attributes"))

    class Meta:
        model = AttributeGroup
        interfaces = (relay.Node,)
        fields = ("uuid", "parent", "name", "attributes")
        filter_fields = ["uuid"]
        description = _("groups of attributes")

    def resolve_attributes(self, info):
        product_uuid = getattr(info.context, "_product_uuid", None)
        qs = self.attributes.all()

        if product_uuid:
            qs = qs.filter(values__product__uuid=product_uuid).distinct()

        return qs


class BrandType(DjangoObjectType):
    categories = List(lambda: CategoryType, description=_("categories"))

    class Meta:
        model = Brand
        interfaces = (relay.Node,)
        fields = ("uuid", "categories", "name")
        filter_fields = ["uuid"]
        description = _("brands")

    def resolve_categories(self, info):
        if info.context.user.has_perm("core.view_category"):
            return self.categories.all()
        return self.categories.filter(is_active=True)


class FilterableAttributeType(ObjectType):
    attribute_name = String(required=True)
    possible_values = List(String, required=True)


class MinMaxPriceType(ObjectType):
    min_price = Float()
    max_price = Float()


class CategoryType(DjangoObjectType):
    children = List(
        lambda: CategoryType,
        depth=Int(default_value=None),
        description=_("categories"),
    )
    image = String(description=_("category image url"))
    markup_percent = Float(required=False, description=_("markup percentage"))
    filterable_attributes = List(
        NonNull(FilterableAttributeType),
        description=_("which attributes and values can be used for filtering this category."),
    )
    min_max_prices = Field(
        NonNull(MinMaxPriceType),
        description=_("minimum and maximum prices for products in this category, if available."),
    )

    class Meta:
        model = Category
        interfaces = (relay.Node,)
        fields = (
            "uuid",
            "markup_percent",
            "attributes",
            "children",
            "name",
            "description",
            "image",
            "min_max_prices",
        )
        filter_fields = ["uuid"]
        description = _("categories")

    def resolve_children(self, info, depth=None) -> TreeQuerySet:
        max_depth = self.get_tree_depth()

        if depth is None:
            depth = max_depth

        if depth <= 0:
            return Category.objects.none()

        categories = Category.objects.language(info.context.locale).filter(parent=self)
        if info.context.user.has_perm("core.view_category"):
            return categories
        return categories.filter(is_active=True)

    def resolve_image(self, info) -> str:
        return info.context.build_absolute_uri(self.image.url) if self.image else ""

    def resolve_markup_percent(self, info) -> float:
        if info.context.user.has_perm("core.view_category"):
            return float(self.markup_percent)
        return 0.0

    def resolve_filterable_attributes(self, info):
        filterable_results = cache.get(f"{self.uuid}_filterable_results", [])

        if len(filterable_results) > 0:
            return filterable_results

        for attr in (
                self.attributes.all()
                if info.context.user.has_perm("view_attribute")
                else self.attributes.filter(is_active=True)
        ):
            distinct_vals = (
                AttributeValue.objects.annotate(value_length=Length("value"))
                .filter(attribute=attr, product__category=self, value_length__lte=30)
                .values_list("value", flat=True)
                .distinct()
            )

            distinct_vals_list = list(distinct_vals)

            if len(distinct_vals_list) <= 128:
                filterable_results.append(
                    FilterableAttributeType(attribute_name=attr.name, possible_values=distinct_vals_list)
                )
            else:
                pass

        cache.set(f"{self.uuid}_filterable_results", filterable_results, 86400)

        return filterable_results

    def resolve_min_max_prices(self, info):
        min_max_prices = cache.get(key=f"{self.name}_min_max_prices", default={})

        if not min_max_prices:
            price_aggregation = Product.objects.filter(category=self).aggregate(
                min_price=Min("stocks__price"), max_price=Max("stocks__price")
            )
            min_max_prices["min_price"] = price_aggregation.get("min_price", 0.0)
            min_max_prices["max_price"] = price_aggregation.get("max_price", 0.0)

            cache.set(key=f"{self.name}_min_max_prices", value=min_max_prices, timeout=86400)

        return MinMaxPriceType(min_price=min_max_prices["min_price"], max_price=min_max_prices["max_price"])


class VendorType(DjangoObjectType):
    markup_percent = Float(description=_("markup percentage"))

    class Meta:
        model = Vendor
        interfaces = (relay.Node,)
        fields = ("uuid", "name", "markup_percent")
        filter_fields = ["uuid"]
        description = _("vendors")


class FeedbackType(DjangoObjectType):
    comment = String(description=_("comment"))
    rating = Int(description=_("rating value from 1 to 10, inclusive, or 0 if not set."))

    class Meta:
        model = Feedback
        interfaces = (relay.Node,)
        fields = ("uuid", "comment", "rating")
        filter_fields = ["uuid"]
        description = _("represents feedback from a user.")


class OrderProductType(DjangoObjectType):
    attributes = GenericScalar(description=_("attributes"))
    notifications = GenericScalar(description=_("notifications"))
    download_url = String(description=_("download url for this order product if applicable"))

    class Meta:
        model = OrderProduct
        interfaces = (relay.Node,)
        fields = (
            "uuid",
            "product",
            "quantity",
            "status",
            "comments",
            "attributes",
            "notifications",
        )
        filter_fields = ["uuid"]
        description = _("order products")

    def resolve_attributes(self, info):
        return camelize(self.attributes)

    def resolve_notifications(self, info):
        return camelize(self.notifications)

    def resolve_download_url(self, info) -> str | None:
        return self.download_url


class OrderType(DjangoObjectType):
    order_products = DjangoFilterConnectionField(
        OrderProductType, description=_("a list of order products in this order")
    )
    billing_address = Field(AddressType, description=_("billing address"))
    shipping_address = Field(
        AddressType,
        description=_("shipping address for this order, leave blank if same as billing address or if not applicable"),
    )
    total_price = Float(description=_("total price of this order"))
    total_quantity = Int(description=_("total quantity of products in order"))
    is_whole_digital = Float(description=_("are all products in the order digital"))
    attributes = GenericScalar(description=_("attributes"))
    notifications = GenericScalar(description=_("notifications"))

    class Meta:
        model = Order
        interfaces = (relay.Node,)
        fields = (
            "uuid",
            "billing_address",
            "shipping_address",
            "status",
            "promo_code",
            "buy_time",
            "user",
            "total_price",
            "total_quantity",
            "is_whole_digital",
        )
        description = _("orders")

    def resolve_total_price(self, _info):
        return self.total_price

    def resolve_total_quantity(self, _info):
        return self.total_quantity

    def resolve_notifications(self, info):
        return camelize(self.notifications)

    def resolve_attributes(self, info):
        return camelize(self.attributes)


class ProductImageType(DjangoObjectType):
    image = String(description=_("image url"))

    class Meta:
        model = ProductImage
        interfaces = (relay.Node,)
        fields = ("uuid", "alt", "priority", "image")
        filter_fields = ["uuid"]
        description = _("product's images")

    def resolve_image(self, info):
        return info.context.build_absolute_uri(self.image.url) if self.image else ""


class ProductType(DjangoObjectType):
    category = Field(CategoryType, description=_("category"))
    images = DjangoFilterConnectionField(ProductImageType, description=_("images"))
    feedbacks = DjangoFilterConnectionField(FeedbackType, description=_("feedbacks"))
    brand = Field(BrandType, description=_("brand"))
    attribute_groups = DjangoFilterConnectionField(AttributeGroupType, description=_("attribute groups"))
    price = Float(description=_("price"))
    quantity = Float(description=_("quantity"))
    feedbacks_count = Int(description=_("number of feedbacks"))

    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = (
            "uuid",
            "category",
            "brand",
            "tags",
            "name",
            "description",
            "feedbacks",
            "images",
            "price",
        )
        filter_fields = ["uuid", "name"]
        description = _("products")

    def resolve_price(self, _info) -> float:
        return self.price or 0.0

    def resolve_feedbacks(self, _info) -> QuerySet[Feedback]:
        if _info.context.user.has_perm("core.view_feedback"):
            return Feedback.objects.filter(order_product__product=self)
        return Feedback.objects.filter(order_product__product=self, is_active=True)

    def resolve_feedbacks_count(self, _info) -> int:
        return self.feedbacks_count or 0

    def resolve_attribute_groups(self, info):
        info.context._product_uuid = self.uuid

        return AttributeGroup.objects.filter(attributes__values__product=self).distinct()

    def resolve_quantity(self, _info) -> int:
        return self.quantity or 0


class AttributeValueType(DjangoObjectType):
    value = String(description=_("attribute value"))

    class Meta:
        model = AttributeValue
        interfaces = (relay.Node,)
        fields = ("uuid", "value")
        filter_fields = ["uuid", "value"]
        description = _("attribute value")


class PromoCodeType(DjangoObjectType):
    discount = Float()
    discount_type = String()

    class Meta:
        model = PromoCode
        interfaces = (relay.Node,)
        fields = (
            "uuid",
            "code",
            "start_time",
            "end_time",
            "used_on",
        )
        filter_fields = ["uuid"]
        description = _("promocodes")

    def resolve_discount(self, info) -> float:
        return self.discount_percent if self.discount_percent else self.discount_amount

    def resolve_discount_type(self, info) -> str:
        return "percent" if self.discount_percent else "amount"


class PromotionType(DjangoObjectType):
    products = DjangoFilterConnectionField(ProductType, description=_("products on sale"))

    class Meta:
        model = Promotion
        interfaces = (relay.Node,)
        fields = ("uuid", "name", "discount_percent", "products")
        filter_fields = ["uuid"]
        description = _("promotions")


class StockType(DjangoObjectType):
    vendor = Field(VendorType, description=_("vendor"))
    product = Field(ProductType, description=_("product"))

    class Meta:
        model = Stock
        interfaces = (relay.Node,)
        fields = ("uuid", "vendor", "product", "price", "quantity", "sku")
        filter_fields = ["uuid"]
        description = _("stocks")


class WishlistType(DjangoObjectType):
    products = DjangoFilterConnectionField(ProductType, description=_("wishlisted products"))

    class Meta:
        model = Wishlist
        interfaces = (relay.Node,)
        fields = ("uuid", "products", "user")
        description = _("wishlists")


class ConfigType(ObjectType):
    project_name = String(description=_("project name"))
    base_domain = String(description=_("company email"))
    company_name = String(description=_("company name"))
    company_address = String(description=_("company address"))
    company_phone_number = String(description=_("company phone number"))
    email_from = String(description=_("email from, sometimes it must be used instead of host user value"))
    email_host_user = String(description=_("email host user"))
    payment_gateway_maximum = Float(description=_("maximum amount for payment"))
    payment_gateway_minimum = Float(description=_("minimum amount for payment"))

    class Meta:
        description = _("company configuration")


class LanguageType(ObjectType):
    code = String(description=_("language code"))
    name = String(description=_("language name"))
    flag = String(description=_("language flag, if exists :)"))

    class Meta:
        description = _("supported languages")


class SearchProductsResultsType(ObjectType):
    uuid = UUID()
    name = String()


class SearchCategoriesResultsType(ObjectType):
    uuid = UUID()
    name = String()


class SearchBrandsResultsType(ObjectType):
    uuid = UUID()
    name = String()


class SearchResultsType(ObjectType):
    products = List(description=_("products search results"), of_type=SearchProductsResultsType)
    categories = List(description=_("products search results"), of_type=SearchCategoriesResultsType)
    brands = List(description=_("products search results"), of_type=SearchBrandsResultsType)
