from uuid import uuid4

import graphene
from django.core.exceptions import PermissionDenied, BadRequest

from core.models import AttributeGroup, Category, Dealer, Feedback, LocalizedAttribute, Order, OrderProduct, \
    PredefinedAttributes, Product, ProductAttribute, ProductImage, PromoCode, Promotion, Stock, Wishlist
from core.object_types import AttributeGroupType, CategoryType, DealerType, FeedbackType, LocalizedAttributeType, \
    OrderType, OrderProductType, PredefinedAttributesType, ProductType, ProductAttributeType, ProductImageType, \
    PromoCodeType, PromotionType, StockType, WishlistType
from geo.models import Address
from geo.object_types import AddressType
from geo.schema import CreateAddress
from payments.models import Transaction, Balance
from payments.object_types import TransactionType, BalanceType
from vibes_auth.models import User
from vibes_auth.object_types import UserType
from vibes_auth.schema import ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken, UpdateUser, CreateUser, \
    DeleteUser


class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info, **kwargs):
        user = info.context.user

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view users.")

        if not (user.is_superuser or user.has_perm('vibes_auth.view_user')):
            raise PermissionDenied("You do not have permission to view users.")

        return User.objects.all()

    user = graphene.Field(UserType, uuid=graphene.UUID(), email=graphene.String())

    def resolve_user(self, info, uuid=None, email=None):

        if (uuid is None or uuid == "") and (email is None or email == ""):
            raise BadRequest("Either uuid or email must be given.")

        if not info.context.user.is_authenticated:
            raise PermissionDenied("You must be logged in to view this user.")

        try:
            if uuid:
                queried_user = User.objects.get(uuid=uuid)
            if email:
                queried_user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise PermissionDenied("No such user exists.")
        else:
            if info.context.user == queried_user or info.context.user.is_superuser or info.context.user.has_perm(
                    'vibes_auth.view_user'):
                return queried_user
        raise PermissionDenied("You do not have permission to view this user's information.")

    attribute_groups = graphene.List(AttributeGroupType)

    def resolve_attribute_groups(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_attribute_group'):
            return AttributeGroup.objects.all()
        return AttributeGroup.objects.filter(active=True)

    addresses = graphene.List(AddressType)

    def resolve_addresses(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('geo.view_address'):
            return Address.objects.all()
        return Address.objects.filter(active=True, user=info.context.user)

    categories = graphene.List(CategoryType)

    def resolve_categories(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_category'):
            return Category.objects.all()
        return Category.objects.filter(active=True)

    dealers = graphene.List(DealerType)

    def resolve_dealers(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_dealer'):
            return Dealer.objects.all()
        return Dealer.objects.none()

    feedbacks = graphene.List(FeedbackType)

    def resolve_feedbacks(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_feedback'):
            return Feedback.objects.all()
        return Feedback.objects.filter(active=True)

    localized_attributes = graphene.List(LocalizedAttributeType)

    def resolve_localized_attributes(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_localized_attribute'):
            return LocalizedAttribute.objects.all()
        return LocalizedAttribute.objects.filter(active=True)

    orders = graphene.List(OrderType)

    def resolve_orders(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_order'):
            return Order.objects.all()
        return Order.objects.filter(active=True, user=info.context.user)

    order_products = graphene.List(OrderProductType)

    def resolve_order_products(self, info, order: uuid4, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_order_product'):
            return OrderProduct.objects.all()
        try:
            return Order.objects.filter(active=True, user=info.context.user, order=Order.objects.get(uuid=order))
        except Order.DoesNotExist:
            raise BadRequest("No such order exists.")

    predefined_attributes = graphene.List(PredefinedAttributesType)

    def resolve_predefined_attributes(self, info, **kwargs):
        return PredefinedAttributes.objects.all()

    products = graphene.List(ProductType)

    def resolve_products(self, info, **kwargs):
        return Product.objects.all()

    product_attributes = graphene.List(ProductAttributeType)

    def resolve_product_attributes(self, info, **kwargs):
        return ProductAttribute.objects.all()

    product_images = graphene.List(ProductImageType)

    def resolve_product_images(self, info, **kwargs):
        return ProductImage.objects.all()

    promo_codes = graphene.List(PromoCodeType)

    def resolve_promo_codes(self, info, **kwargs):
        return PromoCode.objects.all()

    promotions = graphene.List(PromotionType)

    def resolve_promotions(self, info, **kwargs):
        return Promotion.objects.all()

    stocks = graphene.List(StockType)

    def resolve_stocks(self, info, **kwargs):
        return Stock.objects.all()

    wishlists = graphene.List(WishlistType)

    def resolve_wishlists(self, info, **kwargs):
        return Wishlist.objects.all()

    transactions = graphene.List(TransactionType)

    def resolve_transactions(self, info, **kwargs):
        return Transaction.objects.all()

    balances = graphene.Field(BalanceType)

    def resolve_balances(self, info, **kwargs):
        return Balance.objects.all()


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        category_id = graphene.ID(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, category_id, description=None):
        user = info.context.user
        if not info.context.user.is_superuser or not info.context.user.has_perm('vibes_auth.add_product'):
            raise PermissionDenied("You do not have permissions to perform this action.")

        category = Category.objects.get(id=category_id)
        product = Product.objects.create(name=name, description=description, category=category)
        return CreateProduct(product=product)


class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        name = graphene.String()
        description = graphene.String()
        category = graphene.UUID()

    product = graphene.Field(ProductType)

    def mutate(self, info, uuid, name=None, description=None, category=None):

        if not info.context.user.is_superuser or not info.context.user.has_perm('vibes_auth.change_product'):
            raise PermissionDenied("You do not have permissions to perform this action.")

        product = Product.objects.get(id=id)
        if name:
            product.name = name
        if description:
            product.description = description
        if category:
            product.category = Category.objects.get(uuid=category)
        product.save()
        return UpdateProduct(product=product)


class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        if not info.context.user.is_superuser or not info.context.user.has_perm('vibes_auth.delete_product'):
            raise PermissionDenied("You do not have permissions to perform this action.")

        product = Product.objects.get(id=id)
        product.delete()
        return DeleteProduct(ok=True)


class Mutation(graphene.ObjectType):
    obtain_jwt_token = ObtainJSONWebToken.Field()
    refresh_jwt_token = RefreshJSONWebToken.Field()
    verify_jwt_token = VerifyJSONWebToken.Field()
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    create_address = CreateAddress.Field()
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
