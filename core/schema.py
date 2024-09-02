import graphene
from django.core.exceptions import PermissionDenied, BadRequest
from graphene_django.filter import DjangoFilterConnectionField

from core.filters import ProductFilter, OrderFilter
from core.models import (
    AttributeGroup, Category, Dealer, Feedback,
    LocalizedAttribute, Order, OrderProduct, PredefinedAttributes,
    Product, ProductAttribute, ProductImage, PromoCode, Promotion,
    Stock, Wishlist
)
from core.object_types import (
    AttributeGroupType, CategoryType, DealerType, FeedbackType,
    LocalizedAttributeType, OrderType, OrderProductType, PredefinedAttributesType,
    ProductType, ProductAttributeType, ProductImageType, PromoCodeType,
    PromotionType, StockType, WishlistType
)
from geo.models import Address
from geo.object_types import AddressType
from geo.schema import CreateAddress, UpdateAddress, DeleteAddress
from payments.models import Transaction, Balance
from payments.object_types import TransactionType, BalanceType
from vibes_auth.filters import UserFilter
from vibes_auth.models import User
from vibes_auth.object_types import UserType
from vibes_auth.schema import ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken, UpdateUser, CreateUser, \
    DeleteUser


class Query(graphene.ObjectType):
    products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    users = DjangoFilterConnectionField(UserType, filterset_class=UserFilter)
    attribute_groups = DjangoFilterConnectionField(AttributeGroupType)
    addresses = DjangoFilterConnectionField(AddressType)
    categories = DjangoFilterConnectionField(CategoryType)
    dealers = DjangoFilterConnectionField(DealerType)
    feedbacks = DjangoFilterConnectionField(FeedbackType)
    localized_attributes = DjangoFilterConnectionField(LocalizedAttributeType)
    order_products = DjangoFilterConnectionField(OrderProductType)
    predefined_attributes = DjangoFilterConnectionField(PredefinedAttributesType)
    product_attributes = DjangoFilterConnectionField(ProductAttributeType)
    product_images = DjangoFilterConnectionField(ProductImageType)
    promo_codes = DjangoFilterConnectionField(PromoCodeType)
    promotions = DjangoFilterConnectionField(PromotionType)
    stocks = DjangoFilterConnectionField(StockType)
    wishlists = DjangoFilterConnectionField(WishlistType)
    transactions = DjangoFilterConnectionField(TransactionType)
    balances = DjangoFilterConnectionField(BalanceType)

    def resolve_users(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view users.")
        if not (user.is_superuser or user.has_perm('vibes_auth.view_user')):
            return User.objects.filter(uuid=user.uuid)
        return User.objects.all()

    def resolve_attribute_groups(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('core.view_attribute_group'):
            return AttributeGroup.objects.all()
        return AttributeGroup.objects.filter(active=True)

    def resolve_addresses(self, info, **kwargs):
        if info.context.user.is_superuser or info.context.user.has_perm('geo.view_address'):
            return Address.objects.all()
        return Address.objects.filter(active=True, user=info.context.user)

    def resolve_categories(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view categories.")
        if user.is_superuser or user.has_perm('core.view_category'):
            return Category.objects.all()
        return Category.objects.filter(active=True)

    def resolve_dealers(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view dealers.")
        if user.is_superuser or user.has_perm('core.view_dealer'):
            return Dealer.objects.all()
        return Dealer.objects.none()

    def resolve_feedbacks(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view feedback.")
        if user.is_superuser or user.has_perm('core.view_feedback'):
            return Feedback.objects.all()
        return Feedback.objects.filter(order_product__order__user=user, active=True)

    def resolve_localized_attributes(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view localized attributes.")
        if user.is_superuser or user.has_perm('core.view_localized_attribute'):
            return LocalizedAttribute.objects.all()
        return LocalizedAttribute.objects.filter(active=True)

    def resolve_orders(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view orders.")
        if user.is_superuser or user.has_perm('core.view_order'):
            return Order.objects.all()
        return Order.objects.filter(user=user, active=True)

    def resolve_order_products(self, info, order, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view order products.")
        if user.is_superuser or user.has_perm('core.view_order_product'):
            return OrderProduct.objects.filter(order=order)
        return OrderProduct.objects.filter(order__user=user, order=order, active=True)

    def resolve_predefined_attributes(self, info, **kwargs):
        user = info.context.user
        if user.is_superuser or user.has_perm('core.view_predefinedattributes'):
            return PredefinedAttributes.objects.all()
        return PredefinedAttributes.objects.filter(active=True)

    def resolve_products(self, info, **kwargs):
        user = info.context.user
        if user.is_authenticated and user.is_superuser:
            return Product.objects.all()
        return Product.objects.filter(active=True)

    def resolve_product_attributes(self, info, **kwargs):
        user = info.context.user
        if user.is_superuser or user.has_perm('core.view_productattribute'):
            return ProductAttribute.objects.all()
        return ProductAttribute.objects.filter(active=True)

    def resolve_product_images(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view product images.")
        return ProductImage.objects.filter(active=True)

    def resolve_promo_codes(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view promo codes.")
        if user.is_superuser or user.has_perm('core.view_promocode'):
            return PromoCode.objects.all()
        return PromoCode.objects.filter(users__in=[user,])

    def resolve_promotions(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view promotions.")
        if user.is_superuser or user.has_perm('core.view_promotion'):
            return Promotion.objects.all()
        return Promotion.objects.filter(active=True)

    def resolve_stocks(self, info, product, **kwargs):
        user = info.context.user
        return Stock.objects.filter(product=product)

    def resolve_wishlists(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view wishlists.")
        if user.is_superuser or user.has_perm('core.view_wishlist'):
            return Wishlist.objects.all()
        return Wishlist.objects.filter(user=user)

    def resolve_transactions(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view transactions.")
        if user.is_superuser or user.has_perm('payments.view_transaction'):
            return Transaction.objects.all()
        return Transaction.objects.filter(user=user)

    def resolve_balances(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view balances.")
        if user.is_superuser or user.has_perm('payments.view_balance'):
            return Balance.objects.all()
        return Balance.objects.filter(user=user)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        category_id = graphene.UUID(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, category_id, description=None):
        user = info.context.user
        if not user.is_superuser or not user.has_perm('core.add_product'):
            raise PermissionDenied("You do not have permissions to perform this action.")
        category = Category.objects.get(uuid=category_id)
        product = Product.objects.create(name=name, description=description, category=category, active=True)
        return CreateProduct(product=product)


class UpdateProduct(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)
        name = graphene.String()
        description = graphene.String()
        category = graphene.UUID()

    product = graphene.Field(ProductType)

    def mutate(self, info, uuid, name=None, description=None, category=None):
        user = info.context.user
        if not user.is_superuser or not user.has_perm('core.change_product'):
            raise PermissionDenied("You do not have permissions to perform this action.")
        product = Product.objects.get(uuid=uuid)
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
        uuid = graphene.UUID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, uuid):
        user = info.context.user
        if not user.is_superuser or not user.has_perm('core.delete_product'):
            raise PermissionDenied("You do not have permissions to perform this action.")
        product = Product.objects.get(uuid=uuid)
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
    update_address = UpdateAddress.Field()
    delete_address = DeleteAddress.Field()
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
