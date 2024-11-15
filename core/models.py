from django.contrib.postgres.indexes import GinIndex
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    Avg,
    CASCADE,
    CharField,
    DateTimeField,
    DecimalField,
    FloatField,
    ForeignKey,
    ImageField,
    IntegerField,
    JSONField,
    ManyToManyField,
    OneToOneField,
    PROTECT,
    TextField, PositiveIntegerField, UniqueConstraint,
)
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from parler.models import TranslatableModel, TranslatedFields

from core.abstract import NiceModel
from core.choices import ORDER_PRODUCT_STATUS_CHOICES, ORDER_STATUS_CHOICES
from core.utils import get_random_code, get_product_uuid_as_path
from core.utils.lists import FAILED_STATUSES
from core.validators import validate_category_image_dimensions


class AttributeGroup(NiceModel, TranslatableModel):
    translations = TranslatedFields(
        name=CharField(max_length=255, verbose_name=_('name'), help_text=_("Attribute Group's name")),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attribute group")
        verbose_name_plural = _("attribute groups")


class Attribute(NiceModel, TranslatableModel):
    group = ForeignKey('core.AttributeGroup', on_delete=CASCADE, related_name='attributes',
                       help_text=_("Attribute's group"), verbose_name=_('group'))
    value_type = CharField(
        max_length=50,
        choices=[('string', 'String'), ('integer', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean')],
        help_text=_("Attribute's value type"), verbose_name=_('value type'))

    translations = TranslatedFields(
        name=CharField(max_length=255, help_text=_("Attribute's name"), verbose_name=_('name')),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attribute")
        verbose_name_plural = _("attributes")


class AttributeValue(NiceModel, TranslatableModel):
    attribute = ForeignKey('core.Attribute', on_delete=CASCADE, related_name='values',
                           help_text=_("Attribute"), verbose_name=_('attribute'))

    translations = TranslatedFields(
        value=CharField(max_length=255, verbose_name=_('value'), help_text=_("Attribute value")),
    )

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        verbose_name = _("attribute value")
        verbose_name_plural = _("attribute values")


class Category(MPTTModel, NiceModel, TranslatableModel):
    image = ImageField(blank=False, null=True, help_text=_("Category's image"),
                       upload_to='categories/', validators=[validate_category_image_dimensions],
                       verbose_name=_('image'))
    markup_percent = IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("The markup applied to parsed products. Dealers' markups have lower priority"),
        verbose_name=_('markup'))
    parent = TreeForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name='children',
                            help_text=_("Category's parent"), verbose_name=_('parent'))

    translations = TranslatedFields(
        name=CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name")),
        description=TextField(blank=True, null=True, help_text=_("Category's description"), verbose_name=_('description')),
    )

    attributes = ManyToManyField('core.Attribute', through='CategoryAttribute', related_name='categories',
                                 verbose_name=_('attributes'), help_text=_("Attributes associated with the category"))

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)

    class MPTTMeta:
        order_insertion_by = ['translations__name']

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class CategoryAttribute(NiceModel):
    category = ForeignKey('core.Category', on_delete=CASCADE, related_name='self_attributes')
    attribute = ForeignKey('core.Attribute', on_delete=CASCADE, related_name='categorized_attributes',)

    class Meta:
        verbose_name = _("category attribute")
        verbose_name_plural = _("category attributes")
        constraints = [
            UniqueConstraint(fields=['category', 'attribute'], name='unique_category_attribute')
        ]

    def __str__(self):
        return f"{self.category.name} - {self.attribute.name}"


class Brand(NiceModel):
    name = CharField(max_length=255, help_text=_("Brand's name"), verbose_name=_('name'))
    category = ForeignKey('core.Category', on_delete=PROTECT, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')


class Product(NiceModel, TranslatableModel):
    category = ForeignKey('core.Category', on_delete=CASCADE, help_text=_("Product's category"),
                          verbose_name=_('category'))
    brand = ForeignKey('core.Brand', on_delete=CASCADE, blank=True, null=True, help_text=_("Product's brand"))
    tags = ManyToManyField('core.ProductTag', blank=True, help_text=_("Product's tags"), verbose_name=_('tags'))

    translations = TranslatedFields(
        name=CharField(max_length=255, help_text=_("Product's name"), verbose_name=_('name')),
        description=TextField(blank=True, null=True, help_text=_("Product's description"), verbose_name=_('description')),
    )

    attributes = ManyToManyField('core.AttributeValue', through='ProductAttributeValue',
                                 related_name='products', verbose_name=_('attributes'))

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.name

    @property
    def rating(self):
        cache_key = f'product_rating_{self.pk}'
        rating = cache.get(cache_key)
        if rating is None:
            feedbacks = Feedback.objects.filter(order_product__product_id=self.pk)
            rating = feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
            cache.set(cache_key, rating, 604800)
        return round(rating, 2)

    @property
    def price(self) -> float:
        cache_key = f'product_price_{self.pk}'
        price = cache.get(cache_key)
        if price is None:
            stock = self.stocks.order_by('price').only('price').first()
            price = stock.price if stock else 0.0
            cache.set(cache_key, price, 3600)
        return round(price, 2)


class ProductAttributeValue(NiceModel):
    product = ForeignKey('core.Product', on_delete=CASCADE)
    attribute_value = ForeignKey('core.AttributeValue', on_delete=CASCADE)

    class Meta:
        verbose_name = _("product attribute value")
        verbose_name_plural = _("product attribute values")
        constraints = [
            UniqueConstraint(fields=['product', 'attribute_value'], name='unique_product_attribute_value')
        ]

    def __str__(self):
        return f"{self.product.name} - {self.attribute_value}"


class Dealer(NiceModel):
    authentication = JSONField(blank=True, null=True, help_text=_("Authentication info for dealer's endpoints"),
                               verbose_name=_('authentication'))
    markup_percent = IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("The markup applied to parsed products. Categories' markups have higher priority"),
        verbose_name=_('markup'))
    name = CharField(max_length=255, help_text=_("Dealer's name"), verbose_name=_('dealer name'), blank=False,
                     null=False)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _('dealer')
        verbose_name_plural = _('dealers')
        indexes = [
            GinIndex(fields=['authentication']),
        ]


class Feedback(NiceModel):
    comment = TextField(blank=True, null=True, help_text=_("Feedback's text"), verbose_name=_('comment'))
    order_product = OneToOneField('core.OrderProduct', on_delete=CASCADE, blank=False, null=False,
                               help_text=_("Feedback's product"), verbose_name=_('order product'))
    rating = FloatField(blank=True, null=True, help_text=_("Feedback's rating"), verbose_name=_('rating'))

    def __str__(self) -> str:
        return f'{self.rating} by {self.order_product.order.user.email}'

    class Meta:
        verbose_name = _('feedback')
        verbose_name_plural = _('feedbacks')


class Order(NiceModel):
    billing_address = ForeignKey('geo.Address', on_delete=CASCADE, blank=True, null=True,
                                 related_name='billing_address_order', help_text=_("Order's billing address"),
                                 verbose_name=_('billing address'))
    promo_code = ForeignKey('core.PromoCode', on_delete=PROTECT, blank=True, null=True,
                            help_text=_("Order's promo code. May be empty. Do not change after 'finished' status"),
                            verbose_name=_('promo code'))
    shipping_address = ForeignKey('geo.Address', on_delete=CASCADE, blank=True, null=True,
                                  related_name='shipping_address_order', help_text=_("Order's shipping address"),
                                  verbose_name=_('shipping address'))
    status = CharField(
        default="PENDING", max_length=64, choices=ORDER_STATUS_CHOICES, help_text=_("Order's status"),
        verbose_name=_('status'))
    user = ForeignKey('vibes_auth.User', on_delete=CASCADE, help_text=_("Order's user"), verbose_name=_('user'),
                      related_name='orders')
    buy_time = DateTimeField(help_text=_("Order's buy time"), verbose_name=_('buy time'), default=None,
                             null=True, blank=True)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self) -> str:
        return f'{self.pk} Order for {self.user.email}'

    @property
    def total_price(self):
        return round(sum(
            order_product.buy_price * order_product.quantity if order_product.status
                                                                not in FAILED_STATUSES and order_product.buy_price is not None else 0.0
            for order_product in self.order_products.all()), 2) or 0.0

    @property
    def total_quantity(self):
        return sum([order_product.quantity for order_product in self.order_products.all()])

    def add_product(self, product_uuid, attributes):
        try:
            product = Product.objects.get(uuid=product_uuid)
            order_product, is_created = OrderProduct.objects.get_or_create(product=product, order=self,
                                                                           attributes=attributes,
                                                                           defaults={"quantity": 1,
                                                                                     "buy_price": product.price})
            if not is_created:
                order_product.quantity += 1
                order_product.buy_price = product.price
                order_product.save()
        except Product.DoesNotExist:
            raise Http404

    def remove_product(self, product_uuid, attributes):
        try:
            product = Product.objects.get(uuid=product_uuid)
            order_product = self.order_products.get(product=product, order=self, attributes=attributes)
            if order_product.quantity == 1:
                self.order_products.remove(order_product)
                order_product.delete()
            else:
                order_product.quantity -= 1
                order_product.save()
        except Product.DoesNotExist:
            raise Http404

    def remove_all_products(self):
        for order_product in self.order_products.all():
            self.order_products.remove(order_product)
            order_product.delete()

        return self

    def remove_products_of_a_kind(self, product_uuid, attributes):
        try:
            product = Product.objects.get(uuid=product_uuid)
            order_product = self.order_products.get(product=product, order=self, attributes=attributes)
            self.order_products.remove(order_product)
            order_product.delete()
        except Product.DoesNotExist:
            raise Http404

        return self


class OrderProduct(NiceModel):
    buy_price = FloatField(blank=True, null=True, help_text=_("The price the customer paid when bought the order"),
                           verbose_name=_('buy price'))
    comments = TextField(blank=True, null=True, help_text=_("Order-product's comments. Visible only to admins"),
                         verbose_name=_('comments'))
    notifications = JSONField(blank=True, null=True,
                              help_text=_("Order-product's notifications. Displayed to user's on the storefront"),
                              verbose_name=_('notifications'))
    attributes = JSONField(blank=True, null=True,
                           help_text=_("Order-product's notifications. Displayed to user's on the storefront"),
                           verbose_name=_('notifications'))
    order = ForeignKey('core.Order', on_delete=CASCADE, help_text=_("Order"), verbose_name=_('order'),
                       related_name='order_products', null=True)
    product = ForeignKey('core.Product', on_delete=PROTECT, blank=True, null=True, help_text=_("Product"),
                         verbose_name=_('product'))
    quantity = PositiveIntegerField(blank=False, null=False, default=1, help_text=_("Order-product's quantity"), )
    status = CharField(max_length=128, blank=False, null=False, choices=ORDER_PRODUCT_STATUS_CHOICES,
                       help_text=_("Order-product's status"), verbose_name=_('status'), default='PENDING')

    class Meta:
        verbose_name = _("order product")
        verbose_name_plural = _("order products")
        indexes = [
            GinIndex(fields=['notifications', 'attributes']),
        ]


class PredefinedAttributes(NiceModel):
    category = OneToOneField('core.Category', on_delete=CASCADE, related_name='predefined_attributes',
                             help_text=_("Predefined attributes for category"), verbose_name=_('category'))
    groups = ManyToManyField('core.AttributeGroup', related_name='categories',
                             help_text=_("Predefined attribute groups for category"), verbose_name=_('groups'))

    def __str__(self):
        return f"Predefined Attributes for {self.category.name}"

    class Meta:
        verbose_name = _("predefined attribute")
        verbose_name_plural = _("predefined attributes")


class ProductTag(NiceModel, TranslatableModel):
    tag_name = CharField(blank=False, null=False, max_length=255)
    translations = TranslatedFields(
        name=CharField(max_length=255, help_text=_("Product's name"), verbose_name=_('name')),
    )

    def __str__(self):
        return self.tag_name


class ProductAttribute(NiceModel, TranslatableModel):
    group = ForeignKey('core.AttributeGroup', on_delete=CASCADE, related_name='self_attributes',
                       help_text=_("Product attribute's group"), verbose_name=_('group'))
    translations = TranslatedFields(
        name=CharField(max_length=255, help_text=_("Product attribute's name"), verbose_name=_('name')),
        value=CharField(max_length=255, help_text=_("Localized attribute's value"), verbose_name=_('value')),
        description=TextField(blank=True, null=True, help_text=_("Category's description"), verbose_name=_('description')),
    )
    value_type = CharField(
        max_length=50,
        choices=[('string', 'String'), ('integer', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean')],
        help_text=_("Product attribute's value type"), verbose_name=_('value type'))

    def __str__(self):
        return f"{self.group.name} - {self.name}"

    class Meta:
        verbose_name = _("product attribute")
        verbose_name_plural = _("product attributes")


class ProductImage(NiceModel):
    alt = CharField(max_length=255, help_text=_("Image's alt text"), verbose_name=_('alt'))
    image = ImageField(help_text=_("Image"), verbose_name=_('image'), upload_to=get_product_uuid_as_path)
    priority = IntegerField(
        default=1, validators=[MinValueValidator(1)],
        help_text=_("Image's priority. 1 means the first displayed image"), verbose_name=_('priority'))
    product = ForeignKey('core.Product', on_delete=CASCADE, help_text=_("Product"), verbose_name=_('product'),
                         related_name='images')

    def get_product_uuid_as_path(self, *args):
        return str(self.product.uuid) + '/' + args[0]

    def __str__(self) -> str:
        return self.alt

    class Meta:
        ordering = ('priority',)
        verbose_name = _('product image')
        verbose_name_plural = _('product images')


class PromoCode(NiceModel):
    code = CharField(max_length=20, unique=True, default=get_random_code, help_text=_("Promocode's code"),
                     verbose_name=_("promo code"))
    discount_amount = DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_(
        "Promocode's discount amount. May be set only if 'discount percent' is empty"),
                                   verbose_name=_("discount amount"))
    discount_percent = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)], blank=True, null=True,
        help_text=_("Promocode's discount percent. May be set only if 'discount amount' is empty"),
        verbose_name=_("discount percent"))
    end_time = DateTimeField(blank=True, null=True, help_text=_("Promocode's end time"), verbose_name=_("end time"))
    start_time = DateTimeField(blank=True, null=True, help_text=_("Promocode's start time"),
                               verbose_name=_("start time"))
    used_on = DateTimeField(blank=True, null=True,
                            help_text=_("Promocode's date of usage. If empty - Promocode was not used"),
                            verbose_name=_("used on"))
    users = ManyToManyField('vibes_auth.User', blank=True, help_text=_("Users which may use this Promocode"),
                            verbose_name=_('users'))

    class Meta:
        verbose_name = _("promo code")
        verbose_name_plural = _("promo codes")

    def save(self, **kwargs):
        if (self.discount_amount is not None and self.discount_percent is not None) or (
                self.discount_amount is None and self.discount_percent is None):
            raise ValidationError(
                _("Discount amount and discount percent are both present or not specified. Only one must be specified"))
        super().save(**kwargs)

    def __str__(self) -> str:
        return self.code


class Promotion(NiceModel):
    discount_percent = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)], help_text=_("Promotion's discount percent"),
        verbose_name=_("Discount Percent"))
    name = CharField(max_length=256, unique=True, help_text=_("Promotion's name"), verbose_name=_("name"))
    products = ManyToManyField('core.Product', blank=True, help_text=_("Promotion's products"),
                               verbose_name=_('products'))

    class Meta:
        verbose_name = _("promotion")
        verbose_name_plural = _("promotions")

    def __str__(self) -> str:
        if self.name:
            return self.name
        return str(self.id)


class Stock(NiceModel):
    dealer = ForeignKey('core.Dealer', on_delete=CASCADE, help_text=_("Dealer"), verbose_name=_('dealer'))
    price = FloatField(default=0.0, help_text=_("Product's price after applying the markup"), verbose_name=_('price'))
    product = ForeignKey('core.Product', on_delete=CASCADE, help_text=_("Product"), verbose_name=_('product'),
                         related_name='stocks')
    purchase_price = FloatField(default=0.0, help_text=_("Product's purchase_price from dealer's endpoint"),
                                verbose_name=_('purchase price'))
    quantity = IntegerField(default=0, help_text=_("Product's quantity in dealer's stock"), verbose_name=_('quantity'))
    sku = CharField(max_length=255, help_text=_("Dealer's SKU"), verbose_name=_('sku'))

    def __str__(self) -> str:
        return f'{self.dealer.name} - {self.product.name}'

    class Meta:
        verbose_name = _('stock')
        verbose_name_plural = _('stocks')


class Wishlist(NiceModel):
    products = ManyToManyField('core.Product', blank=True, help_text=_("User's wishlisted products"),
                               verbose_name=_('products'))
    user = OneToOneField('vibes_auth.User', on_delete=CASCADE, blank=True, null=True, help_text=_("User"),
                         verbose_name=_('user'), related_name='user_related_wishlist')

    def __str__(self):
        return f"{self.user.email}'s wishlist"

    class Meta:
        verbose_name = _("wishlist")
        verbose_name_plural = _("wishlists")

    def add_product(self, product_uuid):
        try:
            self.products.add(Product.objects.get(uuid=product_uuid))
        except Product.DoesNotExist:
            raise Http404

    def remove_product(self, product_uuid):
        try:
            self.products.remove(Product.objects.get(uuid=product_uuid))
        except Product.DoesNotExist:
            raise Http404

    def bulk_add_products(self, product_uuids):
        self.products.add(*Product.objects.filter(uuid__in=product_uuids))

    def bulk_remove_products(self, product_uuids):
        self.products.remove(*Product.objects.filter(uuid__in=product_uuids))
