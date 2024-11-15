# import graphene
# from constance import config
# from django.core.cache import cache
# from django.core.exceptions import PermissionDenied, BadRequest
# from django.http import Http404
# from django.utils.http import urlencode
# from graphene_django.filter import DjangoFilterConnectionField
#
# from core.abstract import BaseMutation
# from core.filters import ProductFilter, OrderFilter, CategoryFilter
# from core.models import (
#     AttributeGroup, Category, Dealer, Feedback,
#     LocalizedAttribute, Order, OrderProduct, PredefinedAttributes,
#     Product, ProductAttribute, ProductImage, PromoCode, Promotion,
#     Stock, Wishlist, Brand
# )
# from core.object_types import (
#     AttributeGroupType, CategoryType, DealerType, FeedbackType,
#     LocalizedAttributeType, OrderType, OrderProductType, PredefinedAttributesType,
#     ProductType, ProductAttributeType, ProductImageType, PromoCodeType,
#     PromotionType, StockType, WishlistType, ConfigType
# )
# from core.utils.teemill import process_order
# from evibes.settings import SIMPLE_JWT, CACHE_TIMEOUT
# from geo.filters import CountryFilter, RegionFilter, CityFilter, PostalCodeFilter
# from geo.models import Address, Country, Region, City, PostalCode
# from geo.object_types import AddressType, CountryType, RegionType, CityType, PostalCodeType
# from geo.schema import CreateAddress, UpdateAddress, DeleteAddress
# from payments.models import Transaction, Balance
# from payments.object_types import TransactionType, BalanceType
# from payments.schema import Deposit
# from vibes_auth.filters import UserFilter
# from vibes_auth.models import User
# from vibes_auth.object_types import UserType
# from vibes_auth.schema import ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken, UpdateUser, CreateUser, \
#     DeleteUser, ActivateUser, ResetPassword, ConfirmResetPassword
#
#
# class CreateProduct(BaseMutation):
#     class Arguments:
#         name = graphene.String(required=True)
#         description = graphene.String()
#         category_uuid = graphene.UUID(required=True)
#
#     product = graphene.Field(ProductType)
#
#     @staticmethod
#     def mutate(_parent, info, name, category_uuid, description=None):
#         user = info.context.user
#         if not user.is_superuser or not user.has_perm('core.add_product'):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#         category = Category.objects.get(uuid=category_uuid)
#         product = Product.objects.create(name=name, description=description, category=category, active=True)
#         return CreateProduct(product=product)
#
#
# class UpdateProduct(BaseMutation):
#     class Arguments:
#         uuid = graphene.UUID(required=True)
#         name = graphene.String()
#         description = graphene.String()
#         category = graphene.UUID()
#
#     product = graphene.Field(ProductType)
#
#     @staticmethod
#     def mutate(_parent, info, uuid, name=None, description=None, category=None):
#         user = info.context.user
#         if not user.is_superuser or not user.has_perm('core.change_product'):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#         product = Product.objects.get(uuid=uuid)
#         if name:
#             product.name = name
#         if description:
#             product.description = description
#         if category:
#             product.category = Category.objects.get(uuid=category)
#         product.save()
#         return UpdateProduct(product=product)
#
#
# class DeleteProduct(BaseMutation):
#     class Arguments:
#         uuid = graphene.UUID(required=True)
#
#     ok = graphene.Boolean()
#
#     @staticmethod
#     def mutate(_parent, info, uuid):
#         user = info.context.user
#         if not user.is_superuser or not user.has_perm('core.delete_product'):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#         product = Product.objects.get(uuid=uuid)
#         product.delete()
#         return DeleteProduct(ok=True)
#
#
# class AddProductToWishlist(BaseMutation):
#     class Arguments:
#         wishlist_uuid = graphene.UUID(required=True)
#         product_uuid = graphene.UUID(required=True)
#
#     wishlist = graphene.Field(WishlistType)
#
#     @staticmethod
#     def mutate(_parent, info, wishlist_uuid, product_uuid):
#         user = info.context.user
#         wishlist = Wishlist.objects.get(uuid=wishlist_uuid)
#
#         if not (user.is_superuser or user.has_perm('core.change_wishlist') or wishlist.user == user):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#
#         wishlist.products.add(Product.objects.get(uuid=product_uuid))
#         return AddProductToWishlist(wishlist=wishlist)
#
#
# class RemoveProductFromWishlist(BaseMutation):
#     class Arguments:
#         wishlist_uuid = graphene.UUID(required=True)
#         product_uuid = graphene.UUID(required=True)
#
#     wishlist = graphene.Field(WishlistType)
#
#     @staticmethod
#     def mutate(_parent, info, wishlist_uuid, product_uuid):
#         user = info.context.user
#         wishlist = Wishlist.objects.get(uuid=wishlist_uuid)
#
#         if not (user.is_superuser or user.has_perm('core.change_wishlist') or wishlist.user == user):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#
#         wishlist.products.remove(Product.objects.get(uuid=product_uuid))
#         return AddProductToWishlist(wishlist=wishlist)
#
#
# class AddProductToPendingOrder(BaseMutation):
#     class Arguments:
#         order_uuid = graphene.UUID(required=True)
#         product_uuid = graphene.UUID(required=True)
#         size = graphene.String()
#         color = graphene.String()
#
#     order = graphene.Field(OrderType)
#
#     @staticmethod
#     def mutate(_parent, info, product_uuid, order_uuid, size, color):
#         user = info.context.user
#         order = Order.objects.get(uuid=order_uuid)
#
#         if not (user.is_superuser or user.has_perm('core.change_order') or order.user == user):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#
#         order.add_product(product_uuid, size, color)
#
#         return AddProductToPendingOrder(order=order)
#
#
# class RemoveProductFromPendingOrder(BaseMutation):
#     class Arguments:
#         order_uuid = graphene.UUID(required=True)
#         product_uuid = graphene.UUID(required=True)
#         size = graphene.String()
#         color = graphene.String()
#
#     order = graphene.Field(OrderType)
#
#     @staticmethod
#     def mutate(_parent, info, product_uuid, order_uuid, size, color):
#         user = info.context.user
#         order = Order.objects.get(uuid=order_uuid)
#
#         if not (user.is_superuser or user.has_perm('core.change_order') or order.user == user):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#
#         order.remove_product(product_uuid, size, color)
#
#         return AddProductToPendingOrder(order=order)
#
#
# class RemoveAllProductsFromPendingOrder(BaseMutation):
#     class Arguments:
#         order_uuid = graphene.UUID(required=True)
#
#     order = graphene.Field(OrderType)
#
#     @staticmethod
#     def mutate(_parent, info, order_uuid):
#         user = info.context.user
#         order = Order.objects.get(uuid=order_uuid)
#
#         if not (user.is_superuser or user.has_perm('core.change_order') or order.user == user):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#
#         return AddProductToPendingOrder(order=order.remove_all_products())
#
#
# class RemoveAllProductsOfAKindFromPendingOrder(BaseMutation):
#     class Arguments:
#         order_uuid = graphene.UUID(required=True)
#         product_uuid = graphene.UUID(required=True)
#         size = graphene.String()
#         color = graphene.String()
#
#     order = graphene.Field(OrderType)
#
#     @staticmethod
#     def mutate(_parent, info, product_uuid, order_uuid, size, color):
#         user = info.context.user
#         order = Order.objects.get(uuid=order_uuid)
#
#         if not (user.is_superuser or user.has_perm('core.change_order') or order.user == user):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#
#         return AddProductToPendingOrder(order=order.remove_products_of_a_kind(product_uuid, size, color))
#
#
# class BuyOrder(BaseMutation):
#     class Arguments:
#         order_uuid = graphene.UUID(required=True)
#         billing_address_uuid = graphene.UUID(required=True)
#         shipping_address_uuid = graphene.UUID()
#
#     order = graphene.Field(OrderType)
#     transaction = graphene.Field(TransactionType)
#
#     @staticmethod
#     def mutate(_parent, info, order_uuid, billing_address_uuid, shipping_address_uuid=None):
#         user = info.context.user
#
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to buy an order.")
#
#         try:
#
#             order = Order.objects.get(uuid=order_uuid)
#
#             order.billing_address = Address.objects.get(uuid=billing_address_uuid)
#
#             if shipping_address_uuid:
#                 order.shipping_address = Address.objects.get(uuid=shipping_address_uuid)
#
#             order.save()
#
#             if not (user.is_superuser or user.has_perm('core.change_order') or order.user == user):
#                 raise PermissionDenied("You do not have permissions to perform this action.")
#
#             return BuyOrder(process_order(order.uuid))
#
#         except Order.DoesNotExist:
#             raise Http404(f"Order does not exist with the given UUID: {order_uuid}.")
#
#         except Address.DoesNotExist:
#             raise Http404(
#                 f"Address does not exist with the given UUID: {billing_address_uuid | shipping_address_uuid}.")
#
#         except BadRequest:
#             order = Order.objects.get(uuid=order_uuid)
#             order.status = "PAYMENT"
#             order.save()
#             transaction = Transaction.objects.create(balance=order.user.payments_balance, amount=order.total_price,
#                                                      order=order)
#             return Deposit(transaction=transaction)
#
#
# class Contact(BaseMutation):
#     class Arguments:
#         name = graphene.String(required=True)
#         email = graphene.String(required=True)
#         message = graphene.String(required=True)
#         phone_number = graphene.String()
#
#     success = graphene.Boolean()
#
#     @staticmethod
#     def mutate(_parent, info, name, email, message, **kwargs):
#         return Contact(success=True)
#
#
# class Query(graphene.ObjectType):
#     config = graphene.Field(ConfigType)
#     products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
#     orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
#     users = DjangoFilterConnectionField(UserType, filterset_class=UserFilter)
#     attribute_groups = DjangoFilterConnectionField(AttributeGroupType)
#     addresses = DjangoFilterConnectionField(AddressType)
#     countries = DjangoFilterConnectionField(CountryType, filterset_class=CountryFilter)
#     regions = DjangoFilterConnectionField(RegionType, filterset_class=RegionFilter)
#     cities = DjangoFilterConnectionField(CityType, filterset_class=CityFilter)
#     postal_codes = DjangoFilterConnectionField(PostalCodeType, filterset_class=PostalCodeFilter)
#     categories = DjangoFilterConnectionField(CategoryType, filterset_class=CategoryFilter)
#     dealers = DjangoFilterConnectionField(DealerType)
#     feedbacks = DjangoFilterConnectionField(FeedbackType)
#     localized_attributes = DjangoFilterConnectionField(LocalizedAttributeType)
#     order_products = DjangoFilterConnectionField(OrderProductType)
#     predefined_attributes = DjangoFilterConnectionField(PredefinedAttributesType)
#     product_attributes = DjangoFilterConnectionField(ProductAttributeType)
#     product_images = DjangoFilterConnectionField(ProductImageType)
#     promo_codes = DjangoFilterConnectionField(PromoCodeType)
#     promotions = DjangoFilterConnectionField(PromotionType)
#     stocks = DjangoFilterConnectionField(StockType)
#     wishlists = DjangoFilterConnectionField(WishlistType)
#     transactions = DjangoFilterConnectionField(TransactionType)
#     balances = DjangoFilterConnectionField(BalanceType)
#
#     @staticmethod
#     def resolve_config(_parent, _info, **kwargs):
#         data = {
#             "project_name": config.PROJECT_NAME,
#             "company_email": config.EMAIL_HOST_USER,
#             "company_name": config.COMPANY_NAME,
#             "company_address": config.COMPANY_ADDRESS,
#             "company_phone": config.COMPANY_PHONE_NUMBER,
#         }
#
#         if config.EXPOSE_PAYMENT_URL:
#             data["payment_gateway_url"] = config.PAYMENT_GATEWAY_URL
#
#         return data
#
#     @staticmethod
#     def resolve_countries(_parent, _info, **kwargs):
#         return Country.objects.filter(continent__active=True, active=True)
#
#     @staticmethod
#     def resolve_regions(_parent, _info, **kwargs):
#         return Region.objects.filter(country__continent__active=True, country__active=True, active=True).prefetch_related('country')
#
#     @staticmethod
#     def resolve_cities(_parent, _info, **kwargs):
#         return City.objects.filter(region__country__continent__active=True, region__country__active=True,
#                                    region__active=True, active=True).prefetch_related('country', 'region', 'subregion')
#
#     @staticmethod
#     def resolve_postal_codes(_parent, _info, **kwargs):
#         return PostalCode.objects.filter(country__active=True, active=True).prefetch_related('country', 'region', 'subregion', 'city', 'district')
#
#     @staticmethod
#     def resolve_users(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view users.")
#         if not (user.is_superuser or user.has_perm('vibes_auth.view_user')):
#             return User.objects.filter(uuid=user.uuid)
#         return User.objects.all()
#
#     @staticmethod
#     def resolve_attribute_groups(_parent, info, **kwargs):
#         if info.context.user.is_superuser or info.context.user.has_perm('core.view_attribute_group'):
#             return AttributeGroup.objects.all()
#         return AttributeGroup.objects.filter(active=True)
#
#     @staticmethod
#     def resolve_addresses(_parent, info, **kwargs):
#         if info.context.user.is_superuser or info.context.user.has_perm('geo.view_address'):
#             return Address.objects.all()
#         return Address.objects.filter(user=info.context.user)
#
#     @staticmethod
#     def resolve_categories(_parent, info, **kwargs):
#         user = info.context.user
#         if user.is_superuser or user.has_perm('core.view_category'):
#             return Category.objects.all()
#         return Category.objects.filter(active=True)
#
#     @staticmethod
#     def resolve_dealers(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view dealers.")
#         if user.is_superuser or user.has_perm('core.view_dealer'):
#             return Dealer.objects.all()
#         return Dealer.objects.none()
#
#     @staticmethod
#     def resolve_feedbacks(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view feedback.")
#         if user.is_superuser or user.has_perm('core.view_feedback'):
#             return Feedback.objects.all()
#         return Feedback.objects.filter(order_product__order__user=user, active=True)
#
#     @staticmethod
#     def resolve_localized_attributes(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view localized attributes.")
#         if user.is_superuser or user.has_perm('core.view_localized_attribute'):
#             return LocalizedAttribute.objects.all()
#         return LocalizedAttribute.objects.filter(active=True)
#
#     @staticmethod
#     def resolve_orders(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view orders.")
#         if (user.is_superuser or user.has_perm('core.view_order')) and kwargs.get('all', False):
#             return Order.objects.all()
#         return Order.objects.filter(user=user, active=True)
#
#     @staticmethod
#     def resolve_order_products(_parent, info, order, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view order products.")
#         if user.is_superuser or user.has_perm('core.view_order_product'):
#             return OrderProduct.objects.filter(order=order)
#         return OrderProduct.objects.filter(order__user=user, order=order, active=True)
#
#     @staticmethod
#     def resolve_predefined_attributes(_parent, info, **kwargs):
#         user = info.context.user
#         if user.is_superuser or user.has_perm('core.view_predefinedattributes'):
#             return PredefinedAttributes.objects.all()
#         return PredefinedAttributes.objects.filter(active=True)
#
#     @staticmethod
#     def resolve_products(_parent, info, **kwargs):
#         user = info.context.user
#
#         if user.is_superuser or user.has_perm('core.view_product'):
#             return Product.objects.all().prefetch_related('images', 'stocks')
#
#         cache_key = f'products_cache_{urlencode(kwargs)}'
#
#         cached_data = cache.get(cache_key)
#
#         if cached_data:
#             return cached_data
#
#         if kwargs.get('uuid', None):
#             product = Product.objects.filter(uuid=kwargs.get('uuid')).prefetch_related('images', 'stocks')
#             if user.is_authenticated:
#                 user.add_to_recently_viewed(product.uuid)
#             cache.set(cache_key, product, CACHE_TIMEOUT)
#             return product
#
#         products = Product.objects.filter(
#             active=True, brand__active=True, category__active=True
#         ).prefetch_related('images', 'stocks')
#
#         cache.set(cache_key, products, CACHE_TIMEOUT)
#
#         return products
#
#     @staticmethod
#     def resolve_product_attributes(_parent, info, **kwargs):
#         user = info.context.user
#         if user.is_superuser or user.has_perm('core.view_productattribute'):
#             return ProductAttribute.objects.all()
#         return ProductAttribute.objects.filter(active=True)
#
#     @staticmethod
#     def resolve_product_images(_parent, info, product_uuid=None, **kwargs):
#         if product_uuid:
#             return ProductImage.objects.filter(product__uuid=product_uuid, active=True)
#         return ProductImage.objects.filter(active=True)
#
#     @staticmethod
#     def resolve_promo_codes(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view promo codes.")
#         if user.is_superuser or user.has_perm('core.view_promocode'):
#             return PromoCode.objects.all()
#         return PromoCode.objects.filter(users__in=[user, ])
#
#     @staticmethod
#     def resolve_promotions(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view promotions.")
#         if user.is_superuser or user.has_perm('core.view_promotion'):
#             return Promotion.objects.all()
#         return Promotion.objects.filter(active=True)
#
#     @staticmethod
#     def resolve_stocks(_parent, info, product):
#         user = info.context.user
#
#         if not (user.is_superuser or user.has_perm('core.view_stock')):
#             raise PermissionDenied("You do not have permissions to perform this action.")
#
#         return Stock.objects.filter(product=product)
#
#     @staticmethod
#     def resolve_wishlists(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view wishlists.")
#         if user.is_superuser or user.has_perm('core.view_wishlist'):
#             return Wishlist.objects.all()
#         return Wishlist.objects.filter(user=user)
#
#     @staticmethod
#     def resolve_transactions(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view transactions.")
#         if user.is_superuser or user.has_perm('payments.view_transaction'):
#             return Transaction.objects.all()
#         return Transaction.objects.filter(user=user)
#
#     @staticmethod
#     def resolve_balances(_parent, info, **kwargs):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise PermissionDenied("You must be logged in to view balances.")
#         if user.is_superuser or user.has_perm('payments.view_balance'):
#             return Balance.objects.all()
#         return Balance.objects.filter(user=user)
#
#     @staticmethod
#     def resolve_brands(_parent, info, **kwargs):
#         user = info.context.user
#         if user.is_superuser or user.has_perm('core.view_brand'):
#             return Brand.objects.all()
#         return Brand.objects.filter(active=True)
#
#
# class Mutation(graphene.ObjectType):
#     obtain_jwt_token = ObtainJSONWebToken.Field(description="Obtain a pair of JWT tokens for a registered"
#                                                             " and verified user. Access Token Lifetime is "
#                                                             f"{SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds} seconds. "
#                                                             f"Refresh Token Lifetime is "
#                                                             f"{SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].seconds} seconds.")
#     refresh_jwt_token = RefreshJSONWebToken.Field(description="Refresh a pair of JWT tokens. Access Token Lifetime's "
#                                                               f"{SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds} seconds."
#                                                               f"Refresh Token Lifetime's {SIMPLE_JWT
#                                                               ['REFRESH_TOKEN_LIFETIME'].seconds} seconds.")
#     verify_jwt_token = VerifyJSONWebToken.Field(description="Verify any of JWT tokens.")
#     create_user = CreateUser.Field(description="Create a new user. A verification email will be sent containing the"
#                                                "URL to activate the account.")
#     update_user = UpdateUser.Field(description="Update a user. Not all fields may be updated based on your permissions")
#     delete_user = DeleteUser.Field(description="Delete a user. Not all users may be deleted based on your permissions")
#     activate_user = ActivateUser.Field(description="Activate a user account. b64-encoded UUID and token from "
#                                                    "URL are required.")
#     reset_password = ResetPassword.Field(description="Request the password reset email for the user with given email"
#                                                      "Status won't change if email doesn't exist.")
#     confirm_reset_password = ConfirmResetPassword.Field(description="Confirm the password reset for the user with "
#                                                                     "the given b64-encoded UUID, token and password.")
#     deposit = Deposit.Field(description="Request balance deposit. The redirect URL will be given to you if all "
#                                         "requirements are met.")
#     create_address = CreateAddress.Field()
#     update_address = UpdateAddress.Field()
#     delete_address = DeleteAddress.Field()
#     create_product = CreateProduct.Field()
#     update_product = UpdateProduct.Field()
#     delete_product = DeleteProduct.Field()
#     add_product_to_wishlist = AddProductToWishlist.Field()
#     remove_product_from_wishlist = RemoveProductFromWishlist.Field()
#     buy_order = BuyOrder.Field()
#     add_product_to_pending_order = AddProductToPendingOrder.Field()
#     remove_product_from_pending_order = RemoveProductFromPendingOrder.Field()
#     remove_all_products_from_pending_order = RemoveAllProductsFromPendingOrder.Field()
#     remove_all_products_of_a_kind_from_pending_order = RemoveAllProductsOfAKindFromPendingOrder.Field()
#
#
# schema = graphene.Schema(query=Query, mutation=Mutation)
