import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

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
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class DealerType(DjangoObjectType):
    class Meta:
        model = Dealer
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class FeedbackType(DjangoObjectType):
    class Meta:
        model = Feedback
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class LocalizedAttributeType(DjangoObjectType):
    attribute = graphene.Field(lambda: ProductAttributeType)

    class Meta:
        model = LocalizedAttribute
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class OrderType(DjangoObjectType):
    order_products = DjangoFilterConnectionField(lambda: OrderProductType)
    promo_code = graphene.Field(lambda: PromoCodeType)
    billing_address = graphene.Field(lambda: AddressType)
    shipping_address = graphene.Field(lambda: AddressType)
    total_price = graphene.Float()

    class Meta:
        model = Order
        exclude = ('user',)
        interfaces = (relay.Node,)
        filter_fields = ['active']

    def resolve_order_products(self, info):
        return OrderProduct.objects.filter(order=self, active=True)

    def resolve_total_price(self, info) -> float:
        return self.total_price


class OrderProductType(DjangoObjectType):
    order = graphene.Field(lambda: OrderType)
    product = graphene.Field(lambda: ProductType)

    class Meta:
        model = OrderProduct
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class PredefinedAttributesType(DjangoObjectType):
    category = graphene.Field(lambda: CategoryType)
    groups = graphene.List(lambda: AttributeGroupType)

    class Meta:
        model = PredefinedAttributes
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class ProductType(DjangoObjectType):
    category = graphene.Field(lambda: CategoryType)
    images = DjangoFilterConnectionField(lambda: ProductImageType)
    feedbacks = DjangoFilterConnectionField(lambda: FeedbackType)

    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']

    def resolve_feedbacks(self, info):
        return Feedback.objects.filter(order_product__product=self, active=True)


class ProductAttributeType(DjangoObjectType):
    group = graphene.Field(lambda: AttributeGroupType)

    class Meta:
        model = ProductAttribute
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class ProductImageType(DjangoObjectType):
    product = graphene.Field(lambda: ProductType)

    class Meta:
        model = ProductImage
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class PromoCodeType(DjangoObjectType):
    class Meta:
        model = PromoCode
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class PromotionType(DjangoObjectType):
    products = DjangoFilterConnectionField(lambda: ProductType)

    class Meta:
        model = Promotion
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class StockType(DjangoObjectType):
    dealer = graphene.Field(lambda: DealerType)
    product = graphene.Field(lambda: ProductType)

    class Meta:
        model = Stock
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']


class WishlistType(DjangoObjectType):
    products = DjangoFilterConnectionField(lambda: ProductType)

    class Meta:
        model = Wishlist
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = ['active']
