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
    TextField,
)
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from core.abstract import NiceModel
from core.choices import ORDER_PRODUCT_STATUS_CHOICES, ORDER_STATUS_CHOICES
from core.utils import get_random_code
from core.utils.lists import FAILED_STATUSES
from core.validators import validate_category_image_dimensions
from vibes_auth.models import User


class AttributeGroup(NiceModel):
    name = CharField(max_length=255, help_text=_("Attribute group's name"))
    name_ru = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Russian"))
    name_de = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in German"))
    name_it = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Italian"))
    name_es = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Spanish"))
    name_nl = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Dutch"))
    name_fr = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in French"))
    name_ro = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Romanian"))
    name_pl = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Polish"))
    name_cs = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Czech"))
    name_da = CharField(max_length=255, blank=True, null=True, help_text=_("Attribute group's name in Danish"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attribute group")
        verbose_name_plural = _("attribute groups")


class Category(MPTTModel, NiceModel):
    image = ImageField(blank=False, null=True, help_text=_("Category's image"),
                       upload_to=validate_category_image_dimensions, verbose_name=_('image'))
    markup_percent = IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("The markup applied to parsed products. Dealers' markups have lower priority"),
        verbose_name=_('markup'))
    name = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Russian"))
    name_ru = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Russian"))
    name_de = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in German"))
    name_it = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Italian"))
    name_es = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Spanish"))
    name_nl = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Dutch"))
    name_fr = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in French"))
    name_ro = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Romanian"))
    name_pl = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Polish"))
    name_cs = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Czech"))
    name_da = CharField(max_length=255, verbose_name=_('name'), help_text=_("Category's name in Danish"))
    parent = TreeForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name='children',
                            help_text=_("Category's parent"), verbose_name=_('parent'))

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')


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


class Feedback(NiceModel):
    comment = TextField(blank=True, null=True, help_text=_("Feedback's text"), verbose_name=_('comment'))
    order_product = ForeignKey('core.OrderProduct', on_delete=CASCADE, blank=True, null=True,
                               help_text=_("Feedback's product"), verbose_name=_('order product'))
    rating = FloatField(blank=True, null=True, help_text=_("Feedback's rating"), verbose_name=_('rating'))

    class Meta:
        verbose_name = _('feedback')
        verbose_name_plural = _('feedbacks')


class LocalizedAttribute(NiceModel):
    attribute = OneToOneField('core.ProductAttribute', on_delete=CASCADE, related_name='localizations',
                              help_text=_("Localized attribute"), verbose_name=_('attribute'))
    value = CharField(max_length=255, help_text=_("Localized attribute's value"), verbose_name=_('value'))
    value_ru = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Russian"))
    value_de = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in German"))
    value_it = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Italian"))
    value_es = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Spanish"))
    value_nl = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Dutch"))
    value_fr = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in French"))
    value_ro = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Romanian"))
    value_pl = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Polish"))
    value_cs = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Czech"))
    value_da = CharField(max_length=255, blank=True, null=True, verbose_name=_('value in russian'),
                         help_text=_("Localized attribute's value in Danish"))
    parent = TreeForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name='children',
                            help_text=_("Category's parent"), verbose_name=_('parent'))

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"

    class Meta:
        verbose_name = _("localized attribute")
        verbose_name_plural = _("localized attributes")


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

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self) -> str:
        return f'{self.pk} Order for {self.user.email}'

    @property
    def total_price(self):
        return round(sum(
            order_product.buy_price if order_product.status not in FAILED_STATUSES else 0.0
            for order_product in self.order_products.all()), 2)


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
                       related_name='order_products')
    product = ForeignKey('core.Product', on_delete=PROTECT, blank=True, null=True, help_text=_("Product"),
                         verbose_name=_('product'))
    status = CharField(max_length=128, blank=True, null=True, choices=ORDER_PRODUCT_STATUS_CHOICES,
                       help_text=_("Order-product's status"), verbose_name=_('status'))

    class Meta:
        verbose_name = _("order product")
        verbose_name_plural = _("order products")


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


class Product(NiceModel):
    attributes = JSONField(blank=True, null=True, help_text=_("Product's attributes"), verbose_name=_('attributes'))
    category = ForeignKey('core.Category', on_delete=CASCADE, help_text=_("Product's categories"),
                          verbose_name=_('categories'))
    description = TextField(blank=True, null=True, help_text=_("Product's description"), verbose_name=_('description'))
    images = ManyToManyField('core.ProductImage', blank=True, related_name='related_images',
                             help_text=_("Product's images"), verbose_name=_('images'))
    name = CharField(max_length=255, help_text=_("Product's name"), verbose_name=_('name'))
    tags = TextField(blank=True, help_text=_("Product's tags is a comma-separated list"), verbose_name=_('tags'))

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self) -> str:
        return self.name

    _rating = None

    @property
    def rating(self):
        feedbacks = Feedback.objects.filter(order_product__product_uuid=self.uuid)

        if self._rating is None:
            return round(feedbacks.aggregate(Avg('rating'))['rating__avg'] if feedbacks.exists() else 0)
        else:
            return round(self._rating)

    @rating.setter
    def rating(self, value):
        self._rating = value

    @property
    def price(self) -> float:
        return self.stock_set.order_by('price').first().price


class ProductAttribute(NiceModel):
    group = ForeignKey('core.AttributeGroup', on_delete=CASCADE, related_name='attributes',
                       help_text=_("Product attribute's group"), verbose_name=_('group'))
    name = CharField(max_length=255, help_text=_("Product attribute's name"), verbose_name=_('name'))
    name_ru = CharField(max_length=255, blank=True, null=True, help_text=_("Product attribute's name in Russian"),
                        verbose_name=_('name in russian'))
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
    def get_product_uuid_as_path(self, *args):
        return str(self.product.uuid) + '/' + args[0]

    alt = CharField(max_length=255, help_text=_("Image's alt text"), verbose_name=_('alt'))
    image = ImageField(help_text=_("Image"), verbose_name=_('image'), upload_to=get_product_uuid_as_path)
    priority = IntegerField(
        default=1, validators=[MinValueValidator(1)],
        help_text=_("Image's priority. 1 means the first displayed image"), verbose_name=_('priority'))
    product = ForeignKey('core.Product', on_delete=CASCADE, help_text=_("Product"), verbose_name=_('product'))

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
    product = ForeignKey('core.Product', on_delete=CASCADE, help_text=_("Product"), verbose_name=_('product'))
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
