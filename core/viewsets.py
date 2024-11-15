# core/views.py

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter
)
from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import ProductFilter, CategoryFilter, OrderFilter
from .models import (
    AttributeGroup, Attribute, AttributeValue,
    Category, Brand, Product,
    Dealer, Feedback,
    Order, OrderProduct, ProductTag,
    PromoCode, Promotion,
    Stock, Wishlist, PredefinedAttributes
)
from .permissions import IsOwner
from .serializers import (
    AttributeGroupSerializer, AttributeSerializer, AttributeValueSerializer,
    CategorySerializer, BrandSerializer, ProductSerializer,
    DealerSerializer, FeedbackSerializer,
    OrderSerializer, OrderProductSerializer, ProductTagSerializer,
    PromoCodeSerializer, PromotionSerializer,
    StockSerializer, WishlistSerializer, PredefinedAttributesSerializer
)


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of attribute groups."),
    retrieve=extend_schema(description="Retrieve a specific attribute group."),
)
class AttributeGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttributeGroup.objects.all()
    serializer_class = AttributeGroupSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['translations__name']


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of attributes."),
    retrieve=extend_schema(description="Retrieve a specific attribute."),
)
class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attribute.objects.all().select_related('group')
    serializer_class = AttributeSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['translations__name', 'group__translations__name']
    filterset_fields = ['value_type', 'group__uuid']


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of attribute values."),
    retrieve=extend_schema(description="Retrieve a specific attribute value."),
)
class AttributeValueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttributeValue.objects.all().select_related('attribute', 'attribute__group')
    serializer_class = AttributeValueSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['translations__value', 'attribute__translations__name']
    filterset_fields = ['attribute__uuid']


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of categories.",
        parameters=[
            OpenApiParameter(name='uuid', description='Filter by UUID', required=False, type=OpenApiTypes.UUID),
            OpenApiParameter(name='name', description='Filter by category name', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='active', description='Filter by active status', required=False, type=OpenApiTypes.BOOL),
            OpenApiParameter(name='search', description='Search categories by name', required=False, type=OpenApiTypes.STR),
        ],
    ),
    retrieve=extend_schema(description="Retrieve a specific category."),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().select_related('parent').prefetch_related('children', 'attributes')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CategoryFilter
    search_fields = ['translations__name']


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of brands."),
    retrieve=extend_schema(description="Retrieve a specific brand."),
)
class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all().select_related('category')
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category__translations__name']


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of products.",
        parameters=[
            OpenApiParameter(name='uuid', description='Filter by UUID', required=False, type=OpenApiTypes.UUID),
            OpenApiParameter(name='name', description='Filter by product name', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='categories', description='Filter by category name', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='tags', description='Filter by tag name', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='min_price', description='Minimum price', required=False, type=OpenApiTypes.FLOAT),
            OpenApiParameter(name='max_price', description='Maximum price', required=False, type=OpenApiTypes.FLOAT),
            OpenApiParameter(name='is_active', description='Filter by active status', required=False, type=OpenApiTypes.BOOL),
            OpenApiParameter(name='brand', description='Filter by brand name', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(
                name='attribute_values',
                description='Filter by attribute value IDs (multiple values separated by commas)',
                required=False,
                type={'type': 'array', 'items': {'type': 'integer'}},
                explode=False,
                style='form'
            ),
            OpenApiParameter(name='order_by', description='Ordering of results', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='search', description='Search products by name', required=False, type=OpenApiTypes.STR),
        ],
    ),
    retrieve=extend_schema(description="Retrieve a specific product."),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().select_related('category', 'brand').prefetch_related(
        'tags', 'images', 'attributes__attribute__group'
    )
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['translations__name', 'category__translations__name', 'brand__name']


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of dealers."),
    retrieve=extend_schema(description="Retrieve a specific dealer."),
    create=extend_schema(description="Create a new dealer."),
    update=extend_schema(description="Update a dealer."),
    partial_update=extend_schema(description="Partially update a dealer."),
    destroy=extend_schema(description="Delete a dealer."),
)
class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of feedbacks."),
    retrieve=extend_schema(description="Retrieve a specific feedback."),
    create=extend_schema(description="Create a new feedback."),
)
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().select_related('order_product__order__user', 'order_product__product')
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['comment', 'order_product__product__translations__name', 'rating']

    def perform_create(self, serializer):
        serializer.save()


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of orders for the authenticated user.",
        parameters=[
            OpenApiParameter(name='uuid', description='Filter by UUID', required=False, type=OpenApiTypes.UUID),
            OpenApiParameter(name='user_email', description='Filter by user email', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='status', description='Filter by status', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='order_by', description='Ordering of results', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='search', description='Search orders by status', required=False, type=OpenApiTypes.STR),
        ],
    ),
    retrieve=extend_schema(description="Retrieve a specific order."),
    create=extend_schema(description="Create a new order."),
)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOwner, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = OrderFilter
    search_fields = ['status', 'user__email']
    queryset = Order.objects.all().select_related('user').prefetch_related('order_products')

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related('order_products')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of order products."),
    retrieve=extend_schema(description="Retrieve a specific order product."),
)
class OrderProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderProduct.objects.filter(order__user=self.request.user).select_related('product', 'order')


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of product tags."),
    retrieve=extend_schema(description="Retrieve a specific product tag."),
)
class ProductTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['translations__name']


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of promo codes."),
    retrieve=extend_schema(description="Retrieve a specific promo code."),
)
class PromoCodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of promotions."),
    retrieve=extend_schema(description="Retrieve a specific promotion."),
)
class PromotionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of stock entries."),
    retrieve=extend_schema(description="Retrieve a specific stock entry."),
)
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all().select_related('dealer', 'product')
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema_view(
    retrieve=extend_schema(description="Retrieve the wishlist of the authenticated user."),
)
class WishlistViewSet(viewsets.GenericViewSet,
                      mixins.RetrieveModelMixin):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Wishlist.objects.all()

    @extend_schema(description="Retrieve the wishlist of the authenticated user.")
    def retrieve(self, request, *args, **kwargs):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @extend_schema(
        description="Add a product to the authenticated user's wishlist.",
        responses={200: WishlistSerializer},
    )
    def add_product(self, request):
        product_uuid = request.data.get('product_uuid')
        try:
            product = Product.objects.get(uuid=product_uuid)
            wishlist = self.get_object()
            wishlist.products.add(product)
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=404)

    @action(detail=True, methods=['post'], url_path='remove_product', permission_classes=[permissions.IsAuthenticated])
    @extend_schema(
        description="Remove a product from the authenticated user's wishlist.",
        responses={200: WishlistSerializer},
    )
    def remove_product(self, request):
        product_uuid = request.data.get('product_uuid')
        try:
            product = Product.objects.get(uuid=product_uuid)
            wishlist = self.get_object()
            wishlist.products.remove(product)
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except (Product.DoesNotExist, Wishlist.DoesNotExist):
            return Response({'detail': 'Product or Wishlist not found.'}, status=404)


@extend_schema_view(
    list=extend_schema(description="Retrieve a list of predefined attributes."),
    retrieve=extend_schema(description="Retrieve a specific predefined attribute."),
)
class PredefinedAttributesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredefinedAttributes.objects.all()
    serializer_class = PredefinedAttributesSerializer
    permission_classes = [permissions.IsAdminUser]

