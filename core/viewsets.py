from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django_ratelimit.decorators import ratelimit
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.renderers import MultiPartRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_xml.renderers import XMLRenderer
from rest_framework_yaml.renderers import YAMLRenderer

from core.docs.drf.viewsets import (
    ATTRIBUTE_GROUP_SCHEMA,
    ATTRIBUTE_SCHEMA,
    ATTRIBUTE_VALUE_SCHEMA,
    CATEGORY_SCHEMA,
    ORDER_SCHEMA,
    WISHLIST_SCHEMA,
)
from core.filters import BrandFilter, CategoryFilter, OrderFilter, ProductFilter
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
from core.permissions import EvibesPermission
from core.serializers import (
    AddOrderProductSerializer,
    AddWishlistProductSerializer,
    AttributeDetailSerializer,
    AttributeGroupDetailSerializer,
    AttributeGroupSimpleSerializer,
    AttributeSimpleSerializer,
    AttributeValueDetailSerializer,
    AttributeValueSimpleSerializer,
    BrandDetailSerializer,
    BrandSimpleSerializer,
    BulkAddWishlistProductSerializer,
    BulkRemoveWishlistProductSerializer,
    BuyOrderSerializer,
    BuyUnregisteredOrderSerializer,
    CategoryDetailSerializer,
    CategorySimpleSerializer,
    FeedbackSimpleSerializer,
    OrderDetailSerializer,
    OrderProductSimpleSerializer,
    OrderSimpleSerializer,
    ProductDetailSerializer,
    ProductImageSimpleSerializer,
    ProductSimpleSerializer,
    ProductTagSimpleSerializer,
    PromoCodeSimpleSerializer,
    PromotionSimpleSerializer,
    RemoveOrderProductSerializer,
    RemoveWishlistProductSerializer,
    StockSimpleSerializer,
    VendorSimpleSerializer,
    WishlistDetailSerializer,
    WishlistSimpleSerializer,
)
from core.utils import format_attributes
from core.utils.messages import permission_denied_message
from payments.serializers import TransactionProcessSerializer


class EvibesViewSet(ModelViewSet):
    action_serializer_classes = {}
    permission_classes = [EvibesPermission]
    renderer_classes = [CamelCaseJSONRenderer, MultiPartRenderer, XMLRenderer, YAMLRenderer]

    def get_serializer_class(self):
        return self.action_serializer_classes.get(self.action, super().get_serializer_class())


@extend_schema_view(**ATTRIBUTE_GROUP_SCHEMA)
class AttributeGroupViewSet(EvibesViewSet):
    queryset = AttributeGroup.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": AttributeGroupSimpleSerializer,
    }


@extend_schema_view(**ATTRIBUTE_SCHEMA)
class AttributeViewSet(EvibesViewSet):
    queryset = Attribute.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group", "value_type", "is_active"]
    serializer_class = AttributeDetailSerializer
    action_serializer_classes = {
        "list": AttributeSimpleSerializer,
    }


@extend_schema_view(**ATTRIBUTE_VALUE_SCHEMA)
class AttributeValueViewSet(EvibesViewSet):
    queryset = AttributeValue.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["attribute", "is_active"]
    serializer_class = AttributeValueDetailSerializer
    action_serializer_classes = {
        "list": AttributeValueSimpleSerializer,
    }


@extend_schema_view(**CATEGORY_SCHEMA)
class CategoryViewSet(EvibesViewSet):
    queryset = Category.objects.all().prefetch_related()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter
    serializer_class = CategoryDetailSerializer
    action_serializer_classes = {
        "list": CategorySimpleSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.filter(parent=None)
        if self.request.user.has_perm("core.view_category"):
            return qs
        return qs.filter(is_active=True)


class BrandViewSet(EvibesViewSet):
    queryset = Brand.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = BrandFilter
    serializer_class = BrandDetailSerializer
    action_serializer_classes = {
        "list": BrandSimpleSerializer,
    }


class ProductViewSet(EvibesViewSet):
    queryset = Product.objects.prefetch_related("tags", "attributes", "stocks", "images").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    serializer_class = ProductDetailSerializer
    action_serializer_classes = {
        "list": ProductSimpleSerializer,
    }


class VendorViewSet(EvibesViewSet):
    queryset = Vendor.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "markup_percent", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": VendorSimpleSerializer,
    }


class FeedbackViewSet(EvibesViewSet):
    queryset = Feedback.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["order_product", "rating", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": FeedbackSimpleSerializer,
    }


@extend_schema_view(**ORDER_SCHEMA)
class OrderViewSet(EvibesViewSet):
    queryset = Order.objects.prefetch_related("order_products").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": OrderSimpleSerializer,
        "buy": OrderDetailSerializer,
        "add_order_product": AddOrderProductSerializer,
        "remove_order_product": RemoveOrderProductSerializer,
    }

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request, *_args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data=OrderDetailSerializer(Order.objects.filter(user=request.user)).data,
        )

    @action(detail=True, methods=["post"], url_path="buy")
    def buy(self, request, *_args, **kwargs):
        serializer = BuyOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(user=request.user, uuid=kwargs.get("order_uuid"))
            instance = order.buy(
                force_balance=serializer.validated_data.get("force_balance"),
                force_payment=serializer.validated_data.get("force_payment"),
                promocode_uuid=serializer.validated_data.get("promocode_uuid"),
            )
            match str(type(instance)):
                case "<class 'payments.models.Transaction'>":
                    return Response(status=status.HTTP_202_ACCEPTED, data=TransactionProcessSerializer(instance).data)
                case "<class 'core.models.Order'>":
                    return Response(status=status.HTTP_200_OK, data=OrderDetailSerializer(instance).data)
                case _:
                    raise TypeError(_(f"wrong type came from order.buy() method: {type(instance)!s}"))
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"], url_path="buy_unregistered")
    @ratelimit(key="ip", rate="2/h", block=True)
    def buy_unregistered(self, request, *_args, **kwargs):
        serializer = BuyUnregisteredOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = Order.objects.create(status="MOMENTAL")
        products = [product.get("product_uuid") for product in serializer.validated_data.get("products")]
        transaction = order.buy_without_registration(
            products=products,
            promocode_uuid=serializer.validated_data.get("promocode_uuid"),
            customer_name=serializer.validated_data.get("customer_name"),
            customer_email=serializer.validated_data.get("customer_email"),
            customer_phone=serializer.validated_data.get("customer_phone"),
            customer_billing_address=serializer.validated_data.get("customer_billing_address"),
            customer_shipping_address=serializer.validated_data.get("customer_shipping_address"),
            payment_method=serializer.validated_data.get("payment_method"),
        )
        return Response(status=status.HTTP_202_ACCEPTED, data=TransactionProcessSerializer(transaction).data)

    @action(detail=True, methods=["post"], url_path="add_order_product")
    def add_order_product(self, request, *_args, **kwargs):
        serializer = AddOrderProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(uuid=kwargs.get("pk"))
            if not (request.user.has_perm("core.add_orderproduct") or request.user == order.user):
                raise PermissionDenied(permission_denied_message)

            order = order.add_product(
                product_uuid=serializer.validated_data.get("product_uuid"),
                attributes=format_attributes(serializer.validated_data.get("attributes")),
            )

            return Response(status=status.HTTP_200_OK, data=OrderDetailSerializer(order).data)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path="remove_order_product")
    def remove_order_product(self, request, *_args, **kwargs):
        serializer = RemoveOrderProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(uuid=kwargs.get("pk"))
            if not (request.user.has_perm("core.add_orderproduct") or request.user == order.user):
                raise PermissionDenied(permission_denied_message)

            order = order.remove_product(
                product_uuid=serializer.validated_data.get("product_uuid"),
                attributes=format_attributes(serializer.validated_data.get("attributes")),
            )

            return Response(status=status.HTTP_200_OK, data=OrderDetailSerializer(order).data)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OrderProductViewSet(EvibesViewSet):
    queryset = OrderProduct.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["order", "product", "status", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": OrderProductSimpleSerializer,
    }


class ProductTagViewSet(EvibesViewSet):
    queryset = ProductTag.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tag_name", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": ProductTagSimpleSerializer,
    }


class ProductImageViewSet(EvibesViewSet):
    queryset = ProductImage.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product", "priority", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": ProductImageSimpleSerializer,
    }


class PromoCodeViewSet(EvibesViewSet):
    queryset = PromoCode.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["code", "discount_amount", "discount_percent", "start_time", "end_time", "used_on", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": PromoCodeSimpleSerializer,
    }


class PromotionViewSet(EvibesViewSet):
    queryset = Promotion.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "discount_percent", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": PromotionSimpleSerializer,
    }


class StockViewSet(EvibesViewSet):
    queryset = Stock.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vendor", "product", "sku", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": StockSimpleSerializer,
    }


@extend_schema_view(**WISHLIST_SCHEMA)
class WishlistViewSet(EvibesViewSet):
    queryset = Wishlist.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "is_active"]
    serializer_class = AttributeGroupDetailSerializer
    action_serializer_classes = {
        "list": WishlistSimpleSerializer,
    }

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request, *_args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data=WishlistDetailSerializer(Wishlist.objects.get(user=request.user)).data,
        )

    @action(detail=True, methods=["post"], url_path="add_wishlist_product")
    def add_wishlist_product(self, request, *_args, **kwargs):
        serializer = AddWishlistProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            wishlist = Wishlist.objects.get(uuid=kwargs.get("pk"))
            if not (request.user.has_perm("core.change_wishlist") or request.user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            wishlist = wishlist.add_product(
                product_uuid=serializer.validated_data.get("product_uuid"),
            )

            return Response(status=status.HTTP_200_OK, data=WishlistDetailSerializer(wishlist).data)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path="remove_wishlist_product")
    def remove_wishlist_product(self, request, *_args, **kwargs):
        serializer = RemoveWishlistProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            wishlist = Wishlist.objects.get(uuid=kwargs.get("pk"))
            if not (request.user.has_perm("core.change_wishlist") or request.user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            wishlist = wishlist.remove_product(
                product_uuid=serializer.validated_data.get("product_uuid"),
            )

            return Response(status=status.HTTP_200_OK, data=WishlistDetailSerializer(wishlist).data)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path="bulk_add_wishlist_product")
    def bulk_add_wishlist_products(self, request, *_args, **kwargs):
        serializer = BulkAddWishlistProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            wishlist = Wishlist.objects.get(uuid=kwargs.get("pk"))
            if not (request.user.has_perm("core.change_wishlist") or request.user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            wishlist = wishlist.bulk_add_products(
                product_uuids=serializer.validated_data.get("product_uuids"),
            )

            return Response(status=status.HTTP_200_OK, data=WishlistDetailSerializer(wishlist).data)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path="bulk_remove_wishlist_product")
    def bulk_remove_wishlist_products(self, request, *_args, **kwargs):
        serializer = BulkRemoveWishlistProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            wishlist = Wishlist.objects.get(uuid=kwargs.get("pk"))
            if not (request.user.has_perm("core.change_wishlist") or request.user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            wishlist = wishlist.bulk_remove_products(
                product_uuids=serializer.validated_data.get("product_uuids"),
            )

            return Response(status=status.HTTP_200_OK, data=WishlistDetailSerializer(wishlist).data)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
