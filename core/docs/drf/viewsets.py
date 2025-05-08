from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status

from core.docs.drf import BASE_ERRORS
from core.serializers import (
    AddOrderProductSerializer,
    AddWishlistProductSerializer,
    AttributeDetailSerializer,
    AttributeGroupDetailSerializer,
    AttributeGroupSimpleSerializer,
    AttributeSimpleSerializer,
    AttributeValueDetailSerializer,
    AttributeValueSimpleSerializer,
    BulkAddWishlistProductSerializer,
    BulkRemoveWishlistProductSerializer,
    BuyOrderSerializer,
    BuyUnregisteredOrderSerializer,
    CategoryDetailSerializer,
    CategorySimpleSerializer,
    OrderDetailSerializer,
    OrderSimpleSerializer,
    ProductDetailSerializer,
    ProductSimpleSerializer,
    RemoveOrderProductSerializer,
    RemoveWishlistProductSerializer,
    WishlistDetailSerializer,
    WishlistSimpleSerializer,
)
from payments.serializers import TransactionProcessSerializer

ATTRIBUTE_GROUP_SCHEMA = {
    "list": extend_schema(
        summary=_("list all attribute groups (simple view)"),
        responses={status.HTTP_200_OK: AttributeGroupSimpleSerializer(many=True), **BASE_ERRORS},
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single attribute group (detailed view)"),
        responses={status.HTTP_200_OK: AttributeGroupDetailSerializer, **BASE_ERRORS},
    ),
    "create": extend_schema(
        summary=_("create an attribute group"),
        responses={status.HTTP_201_CREATED: AttributeGroupDetailSerializer, **BASE_ERRORS},
    ),
    "destroy": extend_schema(
        summary=_("delete an attribute group"),
        responses={status.HTTP_204_NO_CONTENT: {}, **BASE_ERRORS},
    ),
    "update": extend_schema(
        summary=_("rewrite an existing attribute group saving non-editables"),
        responses={status.HTTP_200_OK: AttributeGroupDetailSerializer, **BASE_ERRORS},
    ),
    "partial_update": extend_schema(
        summary=_("rewrite some fields of an existing attribute group saving non-editables"),
        responses={status.HTTP_200_OK: AttributeGroupDetailSerializer, **BASE_ERRORS},
    ),
}

ATTRIBUTE_SCHEMA = {
    "list": extend_schema(
        summary=_("list all attributes (simple view)"),
        responses={status.HTTP_200_OK: AttributeSimpleSerializer(many=True), **BASE_ERRORS},
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single attribute (detailed view)"),
        responses={status.HTTP_200_OK: AttributeDetailSerializer, **BASE_ERRORS},
    ),
    "create": extend_schema(
        summary=_("create an attribute"),
        responses={status.HTTP_201_CREATED: AttributeDetailSerializer, **BASE_ERRORS},
    ),
    "destroy": extend_schema(
        summary=_("delete an attribute"),
        responses={status.HTTP_204_NO_CONTENT: {}, **BASE_ERRORS},
    ),
    "update": extend_schema(
        summary=_("rewrite an existing attribute saving non-editables"),
        responses={status.HTTP_200_OK: AttributeDetailSerializer, **BASE_ERRORS},
    ),
    "partial_update": extend_schema(
        summary=_("rewrite some fields of an existing attribute saving non-editables"),
        responses={status.HTTP_200_OK: AttributeDetailSerializer, **BASE_ERRORS},
    ),
}

ATTRIBUTE_VALUE_SCHEMA = {
    "list": extend_schema(
        summary=_("list all attribute values (simple view)"),
        responses={status.HTTP_200_OK: AttributeValueSimpleSerializer(many=True), **BASE_ERRORS},
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single attribute value (detailed view)"),
        responses={status.HTTP_200_OK: AttributeValueDetailSerializer, **BASE_ERRORS},
    ),
    "create": extend_schema(
        summary=_("create an attribute value"),
        responses={status.HTTP_201_CREATED: AttributeValueDetailSerializer, **BASE_ERRORS},
    ),
    "destroy": extend_schema(
        summary=_("delete an attribute value"),
        responses={status.HTTP_204_NO_CONTENT: {}, **BASE_ERRORS},
    ),
    "update": extend_schema(
        summary=_("rewrite an existing attribute value saving non-editables"),
        responses={status.HTTP_200_OK: AttributeValueDetailSerializer, **BASE_ERRORS},
    ),
    "partial_update": extend_schema(
        summary=_("rewrite some fields of an existing attribute value saving non-editables"),
        responses={status.HTTP_200_OK: AttributeValueDetailSerializer, **BASE_ERRORS},
    ),
}

CATEGORY_SCHEMA = {
    "list": extend_schema(
        summary=_("list all categories (simple view)"),
        responses={status.HTTP_200_OK: CategorySimpleSerializer(many=True), **BASE_ERRORS},
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single category (detailed view)"),
        responses={status.HTTP_200_OK: CategoryDetailSerializer, **BASE_ERRORS},
    ),
    "create": extend_schema(
        summary=_("create a category"),
        responses={status.HTTP_201_CREATED: CategoryDetailSerializer, **BASE_ERRORS},
    ),
    "destroy": extend_schema(
        summary=_("delete a category"),
        responses={status.HTTP_204_NO_CONTENT: {}, **BASE_ERRORS},
    ),
    "update": extend_schema(
        summary=_("rewrite an existing category saving non-editables"),
        responses={status.HTTP_200_OK: CategoryDetailSerializer, **BASE_ERRORS},
    ),
    "partial_update": extend_schema(
        summary=_("rewrite some fields of an existing category saving non-editables"),
        responses={status.HTTP_200_OK: CategoryDetailSerializer, **BASE_ERRORS},
    ),
}

ORDER_SCHEMA = {
    "list": extend_schema(
        summary=_("list all orders (simple view)"),
        description=_("for non-staff users, only their own orders are returned."),
        responses={status.HTTP_200_OK: OrderSimpleSerializer(many=True), **BASE_ERRORS},
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single order (detailed view)"),
        responses={status.HTTP_200_OK: OrderDetailSerializer, **BASE_ERRORS},
    ),
    "create": extend_schema(
        summary=_("create an order"),
        description=_("doesn't work for non-staff users."),
        responses={status.HTTP_201_CREATED: OrderDetailSerializer, **BASE_ERRORS},
    ),
    "destroy": extend_schema(
        summary=_("delete an order"),
        responses={status.HTTP_204_NO_CONTENT: {}, **BASE_ERRORS},
    ),
    "update": extend_schema(
        summary=_("rewrite an existing order saving non-editables"),
        responses={status.HTTP_200_OK: OrderDetailSerializer, **BASE_ERRORS},
    ),
    "partial_update": extend_schema(
        summary=_("rewrite some fields of an existing order saving non-editables"),
        responses={status.HTTP_200_OK: OrderDetailSerializer, **BASE_ERRORS},
    ),
    "buy": extend_schema(
        summary=_("purchase an order"),
        description=_(
            "finalizes the order purchase. if `force_balance` is used,"
            " the purchase is completed using the user's balance;"
            " if `force_payment` is used, a transaction is initiated."
        ),
        request=BuyOrderSerializer,
        responses={
            status.HTTP_200_OK: OrderDetailSerializer,
            status.HTTP_202_ACCEPTED: TransactionProcessSerializer,
            **BASE_ERRORS,
        },
    ),
    "buy_unregistered": extend_schema(
        summary=_("purchase an order without account creation"),
        description=_(
            "finalizes the order purchase for a non-registered user."
        ),
        request=BuyUnregisteredOrderSerializer,
        responses={
            status.HTTP_202_ACCEPTED: TransactionProcessSerializer,
            **BASE_ERRORS,
        },
    ),
    "add_order_product": extend_schema(
        summary=_("add product to order"),
        description=_("adds a product to an order using the provided `product_uuid` and `attributes`."),
        request=AddOrderProductSerializer,
        responses={status.HTTP_200_OK: OrderDetailSerializer, **BASE_ERRORS},
    ),
    "remove_order_product": extend_schema(
        summary=_("remove product from order"),
        description=_("removes a product from an order using the provided `product_uuid` and `attributes`."),
        request=RemoveOrderProductSerializer,
        responses={status.HTTP_200_OK: OrderDetailSerializer, **BASE_ERRORS},
    ),
}

WISHLIST_SCHEMA = {
    "list": extend_schema(
        summary=_("list all wishlists (simple view)"),
        description=_("for non-staff users, only their own wishlists are returned."),
        responses={status.HTTP_200_OK: WishlistSimpleSerializer(many=True), **BASE_ERRORS},
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single wishlist (detailed view)"),
        responses={status.HTTP_200_OK: WishlistDetailSerializer, **BASE_ERRORS},
    ),
    "create": extend_schema(
        summary=_("create an wishlist"),
        description=_("Doesn't work for non-staff users."),
        responses={status.HTTP_201_CREATED: WishlistDetailSerializer, **BASE_ERRORS},
    ),
    "destroy": extend_schema(
        summary=_("delete an wishlist"),
        responses={status.HTTP_204_NO_CONTENT: {}, **BASE_ERRORS},
    ),
    "update": extend_schema(
        summary=_("rewrite an existing wishlist saving non-editables"),
        responses={status.HTTP_200_OK: WishlistDetailSerializer, **BASE_ERRORS},
    ),
    "partial_update": extend_schema(
        summary=_("rewrite some fields of an existing wishlist saving non-editables"),
        responses={status.HTTP_200_OK: WishlistDetailSerializer, **BASE_ERRORS},
    ),
    "add_wishlist_product": extend_schema(
        summary=_("add product to wishlist"),
        description=_("adds a product to an wishlist using the provided `product_uuid`"),
        request=AddWishlistProductSerializer,
        responses={status.HTTP_200_OK: WishlistDetailSerializer, **BASE_ERRORS},
    ),
    "remove_wishlist_product": extend_schema(
        summary=_("remove product from wishlist"),
        description=_("removes a product from an wishlist using the provided `product_uuid`"),
        request=RemoveWishlistProductSerializer,
        responses={status.HTTP_200_OK: WishlistDetailSerializer, **BASE_ERRORS},
    ),
    "bulk_add_wishlist_products": extend_schema(
        summary=_("add many products to wishlist"),
        description=_("adds many products to an wishlist using the provided `product_uuids`"),
        request=BulkAddWishlistProductSerializer,
        responses={status.HTTP_200_OK: WishlistDetailSerializer, **BASE_ERRORS},
    ),
    "bulk_remove_wishlist_products": extend_schema(
        summary=_("remove many products from wishlist"),
        description=_("removes many products from an wishlist using the provided `product_uuids`"),
        request=BulkRemoveWishlistProductSerializer,
        responses={status.HTTP_200_OK: WishlistDetailSerializer, **BASE_ERRORS},
    ),
}

PRODUCT_SCHEMA = {
    "list": extend_schema(
        summary=_("list all products (simple view)"),
        responses={
            status.HTTP_200_OK: ProductSimpleSerializer(many=True),
            **BASE_ERRORS,
        },
    ),
    "retrieve": extend_schema(
        summary=_("retrieve a single product (detailed view)"),
        parameters=[
            OpenApiParameter(
                name="lookup",
                description=_("Product UUID or slug"),
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            status.HTTP_200_OK: ProductDetailSerializer,
            **BASE_ERRORS,
        },
    ),
    "create": extend_schema(
        summary=_("create a product"),
        responses={
            status.HTTP_201_CREATED: ProductDetailSerializer,
            **BASE_ERRORS,
        },
    ),
    "destroy": extend_schema(
        summary=_("delete a product"),
        responses={
            status.HTTP_204_NO_CONTENT: {},
            **BASE_ERRORS,
        },
    ),
    "update": extend_schema(
        summary=_("rewrite an existing product, preserving non-editable fields"),
        responses={
            status.HTTP_200_OK: ProductDetailSerializer,
            **BASE_ERRORS,
        },
    ),
    "partial_update": extend_schema(
        summary=_("update some fields of an existing product, preserving non-editable fields"),
        responses={
            status.HTTP_200_OK: ProductDetailSerializer,
            **BASE_ERRORS,
        },
    ),
}
