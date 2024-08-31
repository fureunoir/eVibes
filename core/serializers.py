from constance import config
from rest_framework.fields import SerializerMethodField, CharField, EmailField, UUIDField, ListField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_recursive.fields import RecursiveField

from core.models import Order, Product, ProductImage, Stock, Category, OrderProduct, PromoCode, \
    PredefinedAttributes, AttributeGroup, LocalizedAttribute, ProductAttribute
from evibes import settings


class StockSerializer(ModelSerializer):
    class Meta:
        model = Stock
        exclude = ('active', 'product', 'dealer', 'purchase_price', 'modified', 'created', 'uuid')


class ProductImageSerialier(ModelSerializer):
    image_url = SerializerMethodField(read_only=True)

    class Meta:
        model = ProductImage
        exclude = ('active', 'product', 'image', 'modified', 'created', 'uuid')

    @staticmethod
    def get_image_url(obj) -> str:
        if obj.image:
            return f'https://{config.BACKEND_DOMAIN}/{settings.MEDIA_URL}/{str(obj.avatar)}'
        return ''


class LocalizedAttributeSerializer(ModelSerializer):
    class Meta:
        model = LocalizedAttribute
        exclude = ('active', 'attribute', 'modified', 'created', 'uuid')


class ProductAttributeSerializer(ModelSerializer):
    localizations = LocalizedAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = ProductAttribute
        exclude = ('active', 'modified', 'created', 'uuid', 'group')


class AttributeGroupSerializer(ModelSerializer):
    attributes = ProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = AttributeGroup
        exclude = ('active', 'modified', 'created', 'uuid')


class PredefinedAttributesSerializer(ModelSerializer):
    groups = AttributeGroupSerializer(many=True, read_only=True)

    class Meta:
        model = PredefinedAttributes
        exclude = ('active', 'category', 'modified', 'created', 'uuid')


class CategorySerializer(ModelSerializer):
    parent = ListField(child=RecursiveField())
    predefined_attributes = PredefinedAttributesSerializer(many=False, read_only=True)

    class Meta:
        model = Category
        exclude = ('active', 'markup_percent', 'modified', 'created')


class ProductSerializer(ModelSerializer):
    stocks_set = StockSerializer(many=True, read_only=True)
    images = ProductImageSerialier(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)
    rating = SerializerMethodField(read_only=True)
    price = SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        exclude = ('active', 'modified', 'created')

    @staticmethod
    def get_rating(obj) -> int:
        return obj.rating | 0

    @staticmethod
    def get_price(obj) -> float:
        return obj.price


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        exclude = ('active', 'order', 'comments', 'modified', 'created')


class PromoCodeSerializer(ModelSerializer):
    class Meta:
        model = PromoCode
        exclude = ('active', 'users')


class OrderSerializer(ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        exclude = ('active', 'user',)


class OrderPromoCodeSerializer(Serializer):
    promo_code = UUIDField(required=False, write_only=True)


class ContactUsSerializer(Serializer):
    email = EmailField(required=True, help_text="Customer's email address.")
    name = CharField(required=False, help_text="Customer's name.")
    subject = CharField(required=False, help_text="Message subject.")
    phone_number = CharField(required=False, help_text="Customer's phone number.")
    message = CharField(required=True, help_text="Message content.")


class ConfirmPasswordResetSerializer(Serializer):
    uidb64 = CharField(write_only=True, required=True)
    token = CharField(write_only=True, required=True)
    password = CharField(write_only=True, required=True)
    confirm_password = CharField(write_only=True, required=True)


class ResetPasswordSerializer(Serializer):
    email = EmailField(write_only=True, required=True)


class ActivateEmailSerializer(Serializer):
    uidb64 = CharField(required=True)
    token = CharField(required=True)


class OrderProductOverwriteSerializer(Serializer):
    product_id = IntegerField(required=True)


class OrderOverwriteSerializer(Serializer):
    products = ListField(child=OrderProductOverwriteSerializer())
