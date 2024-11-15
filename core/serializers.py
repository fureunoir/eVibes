from django.utils.translation import get_language
from rest_framework import serializers

from .models import (
    AttributeGroup, Attribute, AttributeValue,
    Category, Brand, Product,
    Dealer, Feedback,
    Order, OrderProduct, ProductTag,
    ProductImage, PromoCode, Promotion,
    Stock, Wishlist, PredefinedAttributes
)


class TranslatedFieldsMixin:
    context: dict

    def get_translated_field(self, obj, field_name):
        request = self.context.get('request', None)
        language_code = request.LANGUAGE_CODE if request else get_language()
        return obj.safe_translation_getter(field_name, language_code=language_code, any_language=True)


class AttributeGroupSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = AttributeGroup
        fields = ('uuid', 'name')

    def get_name(self, obj) -> str:
        return self.get_translated_field(obj, 'name')


class AttributeSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    group = AttributeGroupSerializer()

    class Meta:
        model = Attribute
        fields = ('uuid', 'name', 'group', 'value_type')

    def get_name(self, obj) -> str:
        return self.get_translated_field(obj, 'name')


class AttributeValueSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    attribute = AttributeSerializer()

    class Meta:
        model = AttributeValue
        fields = ('uuid', 'value', 'attribute')

    def get_value(self, obj) -> str:
        return self.get_translated_field(obj, 'value')


class CategorySerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    attributes = AttributeSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'uuid', 'name', 'description', 'image', 'markup_percent',
            'parent', 'attributes', 'children'
        )

    def get_name(self, obj) -> str:
        return self.get_translated_field(obj, 'name')

    def get_description(self, obj) -> str:
        return self.get_translated_field(obj, 'description')

    def get_parent(self, obj) -> dict | None:
        if obj.parent:
            return {
                'uuid': obj.parent.id,
                'name': self.get_translated_field(obj.parent, 'name')
            }
        return None

    def get_children(self, obj) -> dict | None:
        if obj.has_children:
            serializer = CategoryChildSerializer(obj.get_children(), many=True, context=self.context)
            return serializer.data
        return None


class CategoryChildSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('uuid', 'name')

    def get_name(self, obj) -> str:
        return self.get_translated_field(obj, 'name')


class BrandSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Brand
        fields = ('uuid', 'name', 'category')


class ProductTagSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ProductTag
        fields = ('uuid', 'name')

    def get_name(self, obj) -> str:
        return self.get_translated_field(obj, 'name')


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ('uuid', 'alt', 'priority', 'image_url')

    def get_image_url(self, obj) -> str | None:
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProductSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category = CategorySerializer()
    brand = BrandSerializer()
    tags = ProductTagSerializer(many=True, read_only=True)
    attributes = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)
    price = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = (
            'uuid', 'name', 'description', 'category', 'brand',
            'tags', 'attributes', 'images', 'rating', 'price'
        )

    def get_name(self, obj) -> str:
        return self.get_translated_field(obj, 'name')

    def get_description(self, obj) -> str:
        return self.get_translated_field(obj, 'description')

    def get_attributes(self, obj) -> list[dict] | list:
        attribute_values = obj.attributes.all().select_related('attribute', 'attribute__group')
        attributes = []
        for attribute_value in attribute_values:
            attribute = attribute_value.attribute
            group = attribute.group
            attribute_data = {
                'attribute_id': attribute.id,
                'attribute_name': self.get_translated_field(attribute, 'name'),
                'group_id': group.id,
                'group_name': self.get_translated_field(group, 'name'),
                'value': self.get_translated_field(attribute_value, 'value'),
                'value_id': attribute_value.id,
                'value_type': attribute.value_type
            }
            attributes.append(attribute_data)
        return attributes


class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = ('uuid', 'name', 'markup_percent', 'authentication')


class FeedbackSerializer(serializers.ModelSerializer, TranslatedFieldsMixin):
    order_product = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ('uuid', 'order_product', 'user', 'product', 'comment', 'rating')

    @staticmethod
    def get_user(obj) -> dict:
        return {
            'uuid': obj.order_product.order.user.id,
            'email': obj.order_product.order.user.email
        }

    def get_product(self, obj) -> dict:
        product = obj.order_product.product
        return {
            'uuid': product.id,
            'name': self.get_translated_field(product, 'name')
        }


class OrderProductSerializer(serializers.ModelSerializer, TranslatedFieldsMixin):
    product = ProductSerializer()

    class Meta:
        model = OrderProduct
        fields = (
            'uuid', 'product', 'quantity', 'buy_price',
            'status', 'attributes', 'notifications', 'comments'
        )


class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)
    total_price = serializers.FloatField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'uuid', 'status', 'status_display', 'buy_time',
            'total_price', 'total_quantity', 'order_products'
        )


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = (
            'uuid', 'code', 'discount_amount', 'discount_percent',
            'start_time', 'end_time', 'used_on'
        )


class PromotionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Promotion
        fields = ('uuid', 'name', 'discount_percent', 'products')


class StockSerializer(serializers.ModelSerializer, TranslatedFieldsMixin):
    dealer = DealerSerializer()
    product = ProductSerializer()

    class Meta:
        model = Stock
        fields = ('uuid', 'dealer', 'product', 'sku', 'quantity', 'price', 'purchase_price')


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ('uuid', 'user', 'products')


class PredefinedAttributesSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    groups = AttributeGroupSerializer(many=True, read_only=True)

    class Meta:
        model = PredefinedAttributes
        fields = ('uuid', 'category', 'groups')
