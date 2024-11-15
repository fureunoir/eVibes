# import graphene
# from constance import config
# from graphene import relay, ObjectType
# from graphene.types.generic import GenericScalar
# from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField
#
# from core.models import (
#     AttributeGroup, Category, Dealer, Feedback,
#     LocalizedAttribute, Order, OrderProduct, PredefinedAttributes,
#     Product, ProductAttribute, ProductImage, PromoCode, Promotion,
#     Stock, Wishlist, Brand
# )
# from geo.object_types import AddressType
#
#
# class AttributeGroupType(DjangoObjectType):
#     class Meta:
#         model = AttributeGroup
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class BrandType(DjangoObjectType):
#     class Meta:
#         model = Brand
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class CategoryType(DjangoObjectType):
#     image = graphene.String()
#
#     class Meta:
#         model = Category
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#     def resolve_image(self, info):
#         if self.image:
#             return info.context.build_absolute_uri(self.image.url)
#         else:
#             return ''
#
#
# class DealerType(DjangoObjectType):
#     class Meta:
#         model = Dealer
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class FeedbackType(DjangoObjectType):
#     class Meta:
#         model = Feedback
#         interfaces = (relay.Node,)
#         exclude = ('order_product',)
#         filter_fields = ['uuid', 'active', ]
#
#
# class LocalizedAttributeType(DjangoObjectType):
#     attribute = graphene.Field(lambda: ProductAttributeType, required=False)
#
#     class Meta:
#         model = LocalizedAttribute
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class OrderType(DjangoObjectType):
#     order_products = DjangoFilterConnectionField(lambda: OrderProductType, required=False)
#     promo_code = graphene.Field(lambda: PromoCodeType, required=False)
#     billing_address = graphene.Field(lambda: AddressType, required=False)
#     shipping_address = graphene.Field(lambda: AddressType, required=False)
#     total_price = graphene.Float()
#     total_quantity = graphene.Int()
#
#     class Meta:
#         model = Order
#         exclude = ('payments_transactions',)
#         interfaces = (relay.Node,)
#         filter_fields = ['uuid', 'active', ]
#
#     def resolve_order_products(self, _info):
#         return OrderProduct.objects.filter(order=self, active=True)
#
#     def resolve_total_price(self, _info):
#         return self.total_price
#
#     def resolve_total_quantity(self, _info):
#         return self.total_quantity
#
#
# class OrderProductType(DjangoObjectType):
#     attributes = GenericScalar()
#     notifications = GenericScalar()
#
#     def resolve_attributes(self, _info):
#         return self.attributes
#
#     def resolve_notifications(self, _info):
#         return self.notifications
#
#     class Meta:
#         model = OrderProduct
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class PredefinedAttributesType(DjangoObjectType):
#     category = graphene.Field(lambda: CategoryType, required=False)
#     groups = graphene.List(lambda: AttributeGroupType, required=False)
#
#     class Meta:
#         model = PredefinedAttributes
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class ProductType(DjangoObjectType):
#     category = graphene.Field(lambda: CategoryType, required=False)
#     images = DjangoFilterConnectionField(lambda: ProductImageType, required=False)
#     feedbacks = DjangoFilterConnectionField(lambda: FeedbackType, required=False)
#     brand = graphene.Field(lambda: BrandType, required=False)
#     stocks = DjangoFilterConnectionField(lambda: StockType, required=False)
#     attributes = GenericScalar()
#     price = graphene.Float()
#     quantity = graphene.Int()
#
#     class Meta:
#         model = Product
#         interfaces = (relay.Node,)
#         exclude = ('orderproduct_set', 'promotion_set', 'wishlist_set', 'user_set')
#         filter_fields = ['uuid', 'active', ]
#
#     def resolve_price(self, _info):
#         return Stock.objects.get(product=self, active=True).price if config.STOCKS_ARE_SINGLE else Stock.objects.filter(
#             product=self, active=True).first().price
#
#     def resolve_quantity(self, _info):
#         return Stock.objects.get(product=self,
#                                  active=True).quantity if config.STOCKS_ARE_SINGLE else Stock.objects.filter(
#             product=self, active=True).first().quantity
#
#     def resolve_feedbacks(self, _info):
#         return Feedback.objects.filter(order_product__product=self, active=True)
#
#     def resolve_attributes(self, _info):
#         return self.attributes
#
#
# class ProductAttributeType(DjangoObjectType):
#     group = graphene.Field(lambda: AttributeGroupType)
#
#     class Meta:
#         model = ProductAttribute
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class ProductImageType(DjangoObjectType):
#     product = graphene.Field(lambda: ProductType, required=False)
#     image = graphene.String()
#
#     class Meta:
#         model = ProductImage
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#     def resolve_image(self, info):
#         if self.image:
#             return info.context.build_absolute_uri(self.image.url)
#         else:
#             return ''
#
#
# class PromoCodeType(DjangoObjectType):
#     class Meta:
#         model = PromoCode
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class PromotionType(DjangoObjectType):
#     products = DjangoFilterConnectionField(lambda: ProductType)
#
#     class Meta:
#         model = Promotion
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class StockType(DjangoObjectType):
#     dealer = graphene.Field(lambda: DealerType, required=False)
#     product = graphene.Field(lambda: ProductType, required=False)
#
#     class Meta:
#         model = Stock
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class WishlistType(DjangoObjectType):
#     products = DjangoFilterConnectionField(lambda: ProductType)
#
#     class Meta:
#         model = Wishlist
#         interfaces = (relay.Node,)
#         fields = '__all__'
#         filter_fields = ['uuid', 'active', ]
#
#
# class ConfigType(ObjectType):
#     project_name = graphene.String()
#     company_email = graphene.String()
#     company_name = graphene.String()
#     company_address = graphene.String()
#     company_phone = graphene.String()
#     payment_gateway_url = graphene.String()
