import graphene
from graphene_django import DjangoObjectType

from core.models import (
    AttributeGroup, Category, Dealer, Feedback,
    LocalizedAttribute, Order, OrderProduct, PredefinedAttributes,
    Product, ProductAttribute, ProductImage, PromoCode, Promotion,
    Stock, Wishlist
)
from geo.object_types import AddressType


class AttributeGroupType(DjangoObjectType):
    class Meta:
        model = AttributeGroup


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class DealerType(DjangoObjectType):
    class Meta:
        model = Dealer


class FeedbackType(DjangoObjectType):
    class Meta:
        model = Feedback


class LocalizedAttributeType(DjangoObjectType):
    attribute = graphene.Field(lambda: ProductAttributeType)

    class Meta:
        model = LocalizedAttribute


class OrderType(DjangoObjectType):
    order_products = graphene.List(lambda: OrderProductType)
    promo_code = graphene.Field(lambda: PromoCodeType)
    billing_address = graphene.Field(lambda: AddressType)
    shipping_address = graphene.Field(lambda: AddressType)

    class Meta:
        model = Order
        exclude = ('user',)


class OrderProductType(DjangoObjectType):
    order = graphene.Field(lambda: OrderType)
    product = graphene.Field(lambda: ProductType)

    class Meta:
        model = OrderProduct


class PredefinedAttributesType(DjangoObjectType):
    category = graphene.Field(lambda: CategoryType)
    groups = graphene.List(lambda: AttributeGroupType)

    class Meta:
        model = PredefinedAttributes


class ProductType(DjangoObjectType):
    category = graphene.Field(lambda: CategoryType)
    images = graphene.List(lambda: ProductImageType)
    feedbacks = graphene.List(lambda: FeedbackType)

    class Meta:
        model = Product

    def resolve_feedbacks(self, info):
        return Feedback.objects.filter(order_product__product=self)


class ProductAttributeType(DjangoObjectType):
    group = graphene.Field(lambda: AttributeGroupType)

    class Meta:
        model = ProductAttribute


class ProductImageType(DjangoObjectType):
    product = graphene.Field(lambda: ProductType)

    class Meta:
        model = ProductImage


class PromoCodeType(DjangoObjectType):
    class Meta:
        model = PromoCode


class PromotionType(DjangoObjectType):
    products = graphene.List(lambda: ProductType)

    class Meta:
        model = Promotion


class StockType(DjangoObjectType):
    dealer = graphene.Field(lambda: DealerType)
    product = graphene.Field(lambda: ProductType)

    class Meta:
        model = Stock


class WishlistType(DjangoObjectType):
    products = graphene.List(lambda: ProductType)

    class Meta:
        model = Wishlist
