import logging

from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from graphene import Field, List, ObjectType, Schema
from graphene_django.filter import DjangoFilterConnectionField

from blog.filters import PostFilter
from blog.graphene.object_types import PostType
from core.filters import (
    BrandFilter,
    CategoryFilter,
    FeedbackFilter,
    OrderFilter,
    ProductFilter,
    WishlistFilter,
)
from core.graphene.mutations import (
    AddOrderProduct,
    AddWishlistProduct,
    AutocompleteAddress,
    BuyOrder,
    BuyProduct,
    BuyWishlist,
    CacheOperator,
    ContactUs,
    CreateAddress,
    CreateProduct,
    DeleteAddress,
    DeleteProduct,
    RemoveAllOrderProducts,
    RemoveAllWishlistProducts,
    RemoveOrderProduct,
    RemoveOrderProductsOfAKind,
    RemoveWishlistProduct,
    RequestCursedURL,
    Search,
    UpdateProduct,
)
from core.graphene.object_types import (
    AttributeGroupType,
    BrandType,
    CategoryType,
    ConfigType,
    FeedbackType,
    LanguageType,
    OrderProductType,
    OrderType,
    ProductImageType,
    ProductType,
    PromoCodeType,
    PromotionType,
    StockType,
    VendorType,
    WishlistType,
)
from core.models import (
    AttributeGroup,
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
from core.utils import get_project_parameters
from core.utils.languages import get_flag_by_language
from core.utils.messages import permission_denied_message
from evibes.settings import LANGUAGES
from payments.graphene.mutations import Deposit
from vibes_auth.filters import UserFilter
from vibes_auth.graphene.mutations import (
    ActivateUser,
    ConfirmResetPassword,
    CreateUser,
    DeleteUser,
    ObtainJSONWebToken,
    RefreshJSONWebToken,
    ResetPassword,
    UpdateUser,
    UploadAvatar,
    VerifyJSONWebToken,
)
from vibes_auth.graphene.object_types import UserType
from vibes_auth.models import User

logger = logging.getLogger(__name__)


class Query(ObjectType):
    parameters = Field(ConfigType)
    languages = List(LanguageType)
    products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    users = DjangoFilterConnectionField(UserType, filterset_class=UserFilter)
    attribute_groups = DjangoFilterConnectionField(AttributeGroupType)
    categories = DjangoFilterConnectionField(CategoryType, filterset_class=CategoryFilter)
    vendors = DjangoFilterConnectionField(VendorType)
    feedbacks = DjangoFilterConnectionField(FeedbackType, filterset_class=FeedbackFilter)
    order_products = DjangoFilterConnectionField(OrderProductType)
    product_images = DjangoFilterConnectionField(ProductImageType)
    stocks = DjangoFilterConnectionField(StockType)
    wishlists = DjangoFilterConnectionField(WishlistType, filterset_class=WishlistFilter)
    promotions = DjangoFilterConnectionField(PromotionType)
    promocodes = DjangoFilterConnectionField(PromoCodeType)
    brands = DjangoFilterConnectionField(BrandType, filterset_class=BrandFilter)
    posts = DjangoFilterConnectionField(PostType, filterset_class=PostFilter)

    @staticmethod
    def resolve_parameters(_parent, _info):
        return get_project_parameters()

    @staticmethod
    def resolve_languages(_parent, _info):
        languages = cache.get("languages")

        if not languages:
            languages = [
                {"code": lang[0], "name": lang[1], "flag": get_flag_by_language(lang[0])} for lang in LANGUAGES
            ]
            cache.set("languages", languages, 60 * 60)

        return languages

    @staticmethod
    def resolve_products(_parent, info, **kwargs):
        if info.context.user.is_authenticated and kwargs.get("uuid"):
            product = Product.objects.get(uuid=kwargs["uuid"])
            if product.is_active and product.brand.is_active and product.category.is_active:
                info.context.user.add_to_recently_viewed(product.uuid)
        return (
            Product.objects.all().select_related("brand", "category").prefetch_related("images", "stocks")
            if info.context.user.has_perm("core.view_product")
            else Product.objects.filter(
                is_active=True, brand__is_active=True, category__is_active=True, stocks__isnull=False
            )
            .select_related("brand", "category")
            .prefetch_related("images", "stocks")
        )

    @staticmethod
    def resolve_orders(_parent, info, **kwargs):
        orders = Order.objects
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied(permission_denied_message)

        if user.has_perm("core.view_order"):
            filters = {}
            if kwargs.get("uuid"):
                filters["uuid"] = kwargs["uuid"]
            if kwargs.get("user"):
                filters["user"] = kwargs["user"]
            if kwargs.get("user_email"):
                filters["user__email"] = kwargs["user_email"]
            orders = orders.filter(**filters)
        else:
            filters = {"is_active": True, "user": user}
            if kwargs.get("uuid"):
                filters["uuid"] = kwargs["uuid"]
            orders = orders.filter(**filters)

        return orders

    @staticmethod
    def resolve_users(_parent, info, **kwargs):
        if info.context.user.has_perm("vibes_auth.view_user"):
            return User.objects.all()
        users = User.objects.filter(uuid=info.context.user.pk)
        return users if users.exists() else User.objects.none()

    @staticmethod
    def resolve_attribute_groups(_parent, info, **kwargs):
        if info.context.user.has_perm("core.view_attributegroup"):
            return AttributeGroup.objects.all()
        return AttributeGroup.objects.filter(is_active=True)

    @staticmethod
    def resolve_categories(_parent, info, **kwargs):
        categories = Category.objects.filter(parent=None)
        if info.context.user.has_perm("core.view_category"):
            return categories
        return categories.filter(is_active=True)

    @staticmethod
    def resolve_vendors(_parent, info):
        if not info.context.user.has_perm("core.view_vendor"):
            raise PermissionDenied(permission_denied_message)
        return Vendor.objects.all()

    @staticmethod
    def resolve_brands(_parent, info):
        if not info.context.user.has_perm("core.view_brand"):
            return Brand.objects.filter(is_active=True)
        return Brand.objects.all()

    @staticmethod
    def resolve_feedbacks(_parent, info, **kwargs):
        if info.context.user.has_perm("core.view_feedback"):
            return Feedback.objects.all()
        return Feedback.objects.filter(is_active=True)

    @staticmethod
    def resolve_order_products(_parent, info, **kwargs):
        order_products = OrderProduct.objects
        user = info.context.user

        if user.has_perm("core.view_orderproduct"):
            filters = {}
            if kwargs.get("uuid"):
                filters["uuid"] = kwargs["uuid"]
            if kwargs.get("order"):
                filters["order__uuid"] = kwargs["order"]
            if kwargs.get("user"):
                filters["user__uuid"] = kwargs["user"]
            order_products = order_products.filter(**filters)
        else:
            filters = {"is_active": True, "user": user}
            if kwargs.get("uuid"):
                filters["uuid"] = kwargs["uuid"]
            order_products = order_products.filter(**filters)

        return order_products

    @staticmethod
    def resolve_product_images(_parent, info, **kwargs):
        if info.context.user.has_perm("core.view_productimage"):
            return ProductImage.objects.all()
        return ProductImage.objects.filter(is_active=True)

    @staticmethod
    def resolve_stocks(_parent, info):
        if not info.context.user.has_perm("core.view_stock"):
            raise PermissionDenied(permission_denied_message)
        return Stock.objects.all()

    @staticmethod
    def resolve_wishlists(_parent, info, **kwargs):
        wishlists = Wishlist.objects
        user = info.context.user

        if not user.is_authenticated:
            raise PermissionDenied(permission_denied_message)

        if user.has_perm("core.view_wishlist"):
            filters = {}
            if kwargs.get("uuid"):
                filters["uuid"] = kwargs["uuid"]
            if kwargs.get("user_email"):
                filters["user__email"] = kwargs["user_email"]
            if kwargs.get("user"):
                filters["user__uuid"] = kwargs["user"]
            wishlists = wishlists.filter(**filters)
        else:
            filters = {"is_active": True, "user": user}
            if kwargs.get("uuid"):
                filters["uuid"] = kwargs["uuid"]
            wishlists = wishlists.filter(**filters)

        return wishlists

    @staticmethod
    def resolve_promotions(_parent, info, **kwargs):
        promotions = Promotion.objects
        if info.context.user.has_perm("core.view_promotion"):
            return promotions.all()
        return promotions.filter(is_active=True)

    @staticmethod
    def resolve_promocodes(_parent, info, **kwargs):
        promocodes = PromoCode.objects
        if info.context.user.has_perm("core.view_promocode"):
            return promocodes.filter(user__uuid=kwargs.get("user_uuid")) or promocodes.all()
        return promocodes.filter(is_active=True, user=info.context.user)


class Mutation(ObjectType):
    search = Search.Field()
    cache = CacheOperator.Field()
    request_cursed_URL = RequestCursedURL.Field()  # noqa: N815
    contact_us = ContactUs.Field()
    add_wishlist_product = AddWishlistProduct.Field()
    remove_wishlist_product = RemoveWishlistProduct.Field()
    remove_all_wishlist_products = RemoveAllWishlistProducts.Field()
    buy_wishlist = BuyWishlist.Field()
    add_order_product = AddOrderProduct.Field()
    remove_order_product = RemoveOrderProduct.Field()
    remove_all_order_products = RemoveAllOrderProducts.Field()
    remove_order_products_of_a_kind = RemoveOrderProductsOfAKind.Field()
    buy_order = BuyOrder.Field()
    deposit = Deposit.Field()
    obtain_jwt_token = ObtainJSONWebToken.Field()
    refresh_jwt_token = RefreshJSONWebToken.Field()
    verify_jwt_token = VerifyJSONWebToken.Field()
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    upload_avatar = UploadAvatar.Field()
    activate_user = ActivateUser.Field()
    reset_password = ResetPassword.Field()
    confirm_reset_password = ConfirmResetPassword.Field()
    buy_product = BuyProduct.Field()
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    create_address = CreateAddress.Field()
    delete_address = DeleteAddress.Field()
    autocomplete_address = AutocompleteAddress.Field()


schema = Schema(query=Query, mutation=Mutation)
