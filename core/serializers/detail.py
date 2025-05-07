import logging
from contextlib import suppress
from typing import Optional

from django.core.cache import cache
from django.db.models.functions import Length
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework_recursive.fields import RecursiveField

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
    ProductTag,
    PromoCode,
    Promotion,
    Stock,
    Vendor,
    Wishlist,
)
from core.serializers.simple import CategorySimpleSerializer, ProductSimpleSerializer

logger = logging.getLogger(__name__)


class AttributeGroupDetailSerializer(ModelSerializer):
    children = RecursiveField(many=True)

    class Meta:
        model = AttributeGroup
        fields = [
            "uuid",
            "name",
            "children",
            "created",
            "modified",
        ]


class CategoryDetailSerializer(ModelSerializer):
    children = SerializerMethodField()
    image = SerializerMethodField()
    filterable_attributes = SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "uuid",
            "name",
            "description",
            "image",
            "markup_percent",
            "filterable_attributes",
            "children",
            "created",
            "modified",
        ]

    def get_image(self, obj: Category) -> Optional[str]:
        with suppress(ValueError):
            return obj.image.url
        return None

    def get_filterable_attributes(self, obj: Category) -> list[dict]:
        filterable_results = cache.get(f"{obj.uuid}_filterable_results", [])

        if filterable_results:
            return filterable_results

        request = self.context.get("request")
        user = getattr(request, "user", None)

        attributes = obj.attributes.all() if user.has_perm("view_attribute") else obj.attributes.filter(is_active=True)

        for attr in attributes:
            distinct_vals = (
                AttributeValue.objects.annotate(value_length=Length("value"))
                .filter(attribute=attr, product__category=obj, value_length__lte=30)
                .values_list("value", flat=True)
                .distinct()
            )

            distinct_vals_list = list(distinct_vals)

            if len(distinct_vals_list) <= 256:
                filterable_results.append(
                    {
                        "attribute_name": attr.name,
                        "possible_values": distinct_vals_list,
                        "value_type": attr.value_type,
                    }
                )
            else:
                continue

        cache.set(f"{obj.uuid}_filterable_results", filterable_results, 86400)
        return filterable_results

    def get_children(self, obj) -> list[dict]:
        request = self.context.get("request")
        if request is not None and request.user.has_perm("view_category"):
            children = obj.children.all()
        else:
            children = obj.children.filter(is_active=True)

        if obj.children.exists():
            return (
                CategoryDetailSerializer(children, many=True, context=self.context).data
                if obj.children.exists()
                else []
            )
        else:
            return []


class BrandDetailSerializer(ModelSerializer):
    categories = CategoryDetailSerializer(many=True)
    small_logo = SerializerMethodField()
    big_logo = SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "uuid",
            "name",
            "categories",
            "created",
            "modified",
            "big_logo",
            "small_logo",
        ]

    def get_small_logo(self, obj: Brand) -> Optional[str]:
        with suppress(ValueError):
            return obj.small_logo.url
        return None

    def get_big_logo(self, obj: Brand) -> Optional[str]:
        with suppress(ValueError):
            return obj.big_logo.url
        return None


class ProductTagDetailSerializer(ModelSerializer):
    class Meta:
        model = ProductTag
        fields = [
            "uuid",
            "tag_name",
            "name",
            "created",
            "modified",
        ]


class ProductImageDetailSerializer(ModelSerializer):
    image = SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            "uuid",
            "alt",
            "image",
            "priority",
            "created",
            "modified",
        ]

    def get_image(self, obj: ProductImage) -> str:
        return obj.image.url or ""


class AttributeDetailSerializer(ModelSerializer):
    categories = CategoryDetailSerializer(many=True)
    group = AttributeGroupDetailSerializer()

    class Meta:
        model = Attribute
        fields = [
            "uuid",
            "name",
            "value_type",
            "categories",
            "group",
            "created",
            "modified",
        ]


class AttributeInnerSerializer(ModelSerializer):
    group = AttributeGroupDetailSerializer()

    class Meta:
        model = Attribute
        fields = [
            "uuid",
            "name",
            "value_type",
            "group",
            "created",
            "modified",
        ]


class AttributeValueDetailSerializer(ModelSerializer):
    attribute = AttributeInnerSerializer()

    class Meta:
        model = AttributeValue
        fields = [
            "uuid",
            "attribute",
            "value",
            "created",
            "modified",
        ]


class VendorDetailSerializer(ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "uuid",
            "name",
            "authentication",
            "markup_percent",
            "created",
            "modified",
        ]


class StockDetailSerializer(ModelSerializer):
    vendor = VendorDetailSerializer()

    class Meta:
        model = Stock
        fields = [
            "uuid",
            "vendor",
            "price",
            "purchase_price",
            "quantity",
            "sku",
            "digital_asset",
            "created",
            "modified",
        ]


class PromoCodeDetailSerializer(ModelSerializer):
    class Meta:
        model = PromoCode
        fields = [
            "uuid",
            "code",
            "discount_amount",
            "discount_percent",
            "start_time",
            "end_time",
            "used_on",
            "created",
            "modified",
        ]


class ProductDetailSerializer(ModelSerializer):
    brand = BrandDetailSerializer()
    category = CategorySimpleSerializer()
    tags = ProductTagDetailSerializer(
        many=True,
    )
    images = ProductImageDetailSerializer(
        many=True,
    )
    attributes = AttributeValueDetailSerializer(
        many=True,
    )

    rating = SerializerMethodField()
    price = SerializerMethodField()
    quantity = SerializerMethodField()
    feedbacks_count = SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "uuid",
            "name",
            "description",
            "partnumber",
            "is_digital",
            "brand",
            "category",
            "feedbacks_count",
            "quantity",
            "tags",
            "slug",
            "images",
            "attributes",
            "rating",
            "price",
            "created",
            "modified",
        ]

    def get_rating(self, obj: Product) -> float:
        return obj.rating

    def get_price(self, obj: Product) -> float:
        return obj.price

    def get_feedbacks_count(self, obj: Product) -> int:
        return obj.feedbacks_count

    def get_quantity(self, obj: Product) -> int:
        return obj.quantity


class PromotionDetailSerializer(ModelSerializer):
    products = ProductDetailSerializer(
        many=True,
    )

    class Meta:
        model = Promotion
        fields = [
            "uuid",
            "name",
            "discount_percent",
            "description",
            "products",
            "created",
            "modified",
        ]


class WishlistDetailSerializer(ModelSerializer):
    products = ProductSimpleSerializer(
        many=True,
    )

    class Meta:
        model = Wishlist
        fields = [
            "uuid",
            "products",
            "created",
            "modified",
        ]


class OrderProductDetailSerializer(ModelSerializer):
    product = ProductDetailSerializer()

    class Meta:
        model = OrderProduct
        fields = [
            "uuid",
            "product",
            "quantity",
            "buy_price",
            "comments",
            "notifications",
            "attributes",
            "status",
            "created",
            "modified",
        ]


class FeedbackDetailSerializer(ModelSerializer):
    order_product = OrderProductDetailSerializer()

    class Meta:
        model = Feedback
        fields = [
            "uuid",
            "rating",
            "comment",
            "order_product",
            "created",
            "modified",
        ]


class OrderDetailSerializer(ModelSerializer):
    promo_code = PromoCodeDetailSerializer()
    order_products = OrderProductDetailSerializer(
        many=True,
    )

    class Meta:
        model = Order
        fields = [
            "uuid",
            "status",
            "promo_code",
            "billing_address",
            "shipping_address",
            "buy_time",
            "order_products",
            "human_readable_id",
            "created",
            "modified",
        ]
