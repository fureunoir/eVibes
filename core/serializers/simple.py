from contextlib import suppress
from typing import Optional

from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

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


class AttributeGroupSimpleSerializer(ModelSerializer):
    parent = PrimaryKeyRelatedField(read_only=True)
    children = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = AttributeGroup
        fields = [
            "uuid",
            "name",
            "parent",
            "children",
        ]


class CategorySimpleSerializer(ModelSerializer):
    children = SerializerMethodField()
    image = SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "uuid",
            "name",
            "image",
            "children",
        ]

    def get_image(self, obj: Category) -> Optional[str]:
        with suppress(ValueError):
            return obj.image.url
        return None

    def get_children(self, obj) -> list[dict]:
        request = self.context.get("request")
        if request is not None and request.user.has_perm("view_category"):
            children = obj.children.all()
        else:
            children = obj.children.filter(is_active=True)

        if obj.children.exists():
            return (
                CategorySimpleSerializer(children, many=True, context=self.context).data
                if obj.children.exists()
                else []
            )
        else:
            return []


class BrandSimpleSerializer(ModelSerializer):
    small_logo = SerializerMethodField()
    big_logo = SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "uuid",
            "name",
            "small_logo",
            "big_logo",
        ]

    def get_small_logo(self, obj: Brand) -> Optional[str]:
        with suppress(ValueError):
            return obj.small_logo.url
        return None

    def get_big_logo(self, obj: Brand) -> Optional[str]:
        with suppress(ValueError):
            return obj.big_logo.url
        return None


class ProductTagSimpleSerializer(ModelSerializer):
    class Meta:
        model = ProductTag
        fields = [
            "uuid",
            "tag_name",
            "name",
        ]


class ProductImageSimpleSerializer(ModelSerializer):
    product = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductImage
        fields = [
            "uuid",
            "alt",
            "image",
            "priority",
            "product",
        ]


class AttributeSimpleSerializer(ModelSerializer):
    group = AttributeGroupSimpleSerializer(read_only=True)

    class Meta:
        model = Attribute
        fields = [
            "uuid",
            "name",
            "value_type",
            "group",
        ]


class AttributeValueSimpleSerializer(ModelSerializer):
    attribute = AttributeSimpleSerializer(read_only=True)
    product = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AttributeValue
        fields = [
            "uuid",
            "value",
            "attribute",
            "product",
        ]


class ProductSimpleSerializer(ModelSerializer):
    brand = BrandSimpleSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    tags = ProductTagSimpleSerializer(many=True, read_only=True)
    images = ProductImageSimpleSerializer(many=True, read_only=True)

    attributes = AttributeValueSimpleSerializer(many=True, read_only=True)

    rating = SerializerMethodField()
    price = SerializerMethodField()
    quantity = SerializerMethodField()
    feedbacks_count = SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "uuid",
            "name",
            "is_digital",
            "description",
            "partnumber",
            "brand",
            "feedbacks_count",
            "category",
            "tags",
            "images",
            "attributes",
            "rating",
            "price",
            "quantity",
        ]

    def get_rating(self, obj: Product) -> float:
        return obj.rating

    def get_price(self, obj: Product) -> float:
        return obj.price

    def get_feedbacks_count(self, obj: Product) -> int:
        return obj.feedbacks_count

    def get_quantity(self, obj: Product) -> int:
        return obj.quantity


class VendorSimpleSerializer(ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "uuid",
            "name",
        ]


class StockSimpleSerializer(ModelSerializer):
    vendor = VendorSimpleSerializer(read_only=True)
    product = ProductSimpleSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = [
            "uuid",
            "price",
            "purchase_price",
            "quantity",
            "sku",
            "vendor",
            "product",
        ]


class PromoCodeSimpleSerializer(ModelSerializer):
    class Meta:
        model = PromoCode
        fields = [
            "uuid",
            "code",
        ]


class PromotionSimpleSerializer(ModelSerializer):
    products = ProductSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Promotion
        fields = [
            "uuid",
            "name",
            "discount_percent",
            "products",
        ]


class WishlistSimpleSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)
    products = ProductSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            "uuid",
            "user",
            "products",
        ]


class FeedbackSimpleSerializer(ModelSerializer):
    order_product = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "uuid",
            "rating",
            "order_product",
        ]


class OrderProductSimpleSerializer(ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = [
            "uuid",
            "product",
            "quantity",
            "buy_price",
            "status",
        ]


class OrderSimpleSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)
    promo_code = PromoCodeSimpleSerializer(read_only=True)
    order_products = OrderProductSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "uuid",
            "status",
            "user",
            "promo_code",
            "order_products",
            "buy_time",
        ]
