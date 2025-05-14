import datetime
import json
import logging
from typing import Self

from constance import config
from django.contrib.postgres.indexes import GinIndex
from django.core.cache import cache
from django.core.exceptions import BadRequest, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    PROTECT,
    Avg,
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    FileField,
    FloatField,
    ForeignKey,
    ImageField,
    IntegerField,
    JSONField,
    ManyToManyField,
    Max,
    OneToOneField,
    PositiveIntegerField,
    TextField,
)
from django.http import Http404
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from core.abstract import NiceModel
from core.choices import ORDER_PRODUCT_STATUS_CHOICES, ORDER_STATUS_CHOICES
from core.errors import DisabledCommerceError, NotEnoughMoneyError
from core.utils import generate_human_readable_id, get_product_uuid_as_path, get_random_code
from core.utils.lists import FAILED_STATUSES
from core.validators import validate_category_image_dimensions
from evibes.settings import CURRENCY_CODE
from geo.models import Address, City, Country, PostalCode, Region
from payments.models import Transaction

logger = logging.getLogger(__name__)


class AttributeGroup(NiceModel):
    is_publicly_visible = True

    parent = ForeignKey(
        "self",
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text=_("parent of this group"),
        verbose_name=_("parent attribute group"),
    )
    name = CharField(
        max_length=255,
        verbose_name=_("attribute group's name"),
        help_text=_("attribute group's name"),
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attribute group")
        verbose_name_plural = _("attribute groups")


class Attribute(NiceModel):
    is_publicly_visible = True

    categories = ManyToManyField(
        "core.Category",
        related_name="attributes",
        help_text=_("category of this attribute"),
        verbose_name=_("categories"),
    )

    group = ForeignKey(
        "core.AttributeGroup",
        on_delete=CASCADE,
        related_name="attributes",
        help_text=_("group of this attribute"),
        verbose_name=_("attribute group"),
    )
    value_type = CharField(
        max_length=50,
        choices=[
            ("string", _("string")),
            ("integer", _("integer")),
            ("float", _("float")),
            ("boolean", _("boolean")),
            ("array", _("array")),
            ("object", _("object")),
        ],
        help_text=_("type of the attribute's value"),
        verbose_name=_("value type"),
    )

    name = CharField(
        max_length=255,
        help_text=_("name of this attribute"),
        verbose_name=_("attribute's name"),
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attribute")
        verbose_name_plural = _("attributes")


class AttributeValue(NiceModel):
    is_publicly_visible = True

    attribute = ForeignKey(
        "core.Attribute",
        on_delete=CASCADE,
        related_name="values",
        help_text=_("attribute of this value"),
        verbose_name=_("attribute"),
    )
    product = ForeignKey(
        "core.Product",
        on_delete=CASCADE,
        blank=False,
        null=True,
        help_text=_("the specific product associated with this attribute's value"),
        verbose_name=_("associated product"),
        related_name="attributes",
    )
    value = TextField(
        verbose_name=_("attribute value"),
        help_text=_("the specific value for this attribute"),
    )

    def __str__(self):
        return f"{self.attribute!s}: {self.value}"

    class Meta:
        verbose_name = _("attribute value")
        verbose_name_plural = _("attribute values")


class Category(NiceModel, MPTTModel):
    is_publicly_visible = True

    image = ImageField(
        blank=True,
        null=True,
        help_text=_("upload an image representing this category"),
        upload_to="categories/",
        validators=[validate_category_image_dimensions],
        verbose_name=_("category image"),
    )
    markup_percent = IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("define a markup percentage for products in this category"),
        verbose_name=_("markup percentage"),
    )
    parent = TreeForeignKey(
        "self",
        on_delete=CASCADE,
        blank=True,
        null=True,
        related_name="children",
        help_text=_("parent of this category to form a hierarchical structure"),
        verbose_name=_("parent category"),
    )

    name = CharField(
        max_length=255,
        verbose_name=_("category name"),
        help_text=_("provide a name for this category"),
        unique=True,
    )

    description = TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text=_("add a detailed description for this category"),
        verbose_name=_("category description"),
    )

    def __str__(self):
        return self.name

    def get_tree_depth(self):
        if self.is_leaf_node():
            return 0
        return self.get_descendants().aggregate(max_depth=Max("level"))["max_depth"] - self.get_level()

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["tree_id", "lft"]


class Brand(NiceModel):
    is_publicly_visible = True

    name = CharField(
        max_length=255,
        help_text=_("name of this brand"),
        verbose_name=_("brand name"),
        unique=True,
    )
    small_logo = ImageField(
        upload_to="brands/",
        blank=True,
        null=True,
        help_text=_("upload a logo representing this brand"),
        validators=[validate_category_image_dimensions],
        verbose_name=_("brand small image"),
    )
    big_logo = ImageField(
        upload_to="brands/",
        blank=True,
        null=True,
        help_text=_("upload a big logo representing this brand"),
        validators=[validate_category_image_dimensions],
        verbose_name=_("brand big image"),
    )
    description = TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text=_("add a detailed description of the brand"),
        verbose_name=_("brand description"),
    )
    categories = ManyToManyField(
        "core.Category",
        blank=True,
        help_text=_("optional categories that this brand is associated with"),
        verbose_name=_("associated categories"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("brand")
        verbose_name_plural = _("brands")


class Product(NiceModel):
    is_publicly_visible = True

    category = ForeignKey(
        "core.Category",
        on_delete=CASCADE,
        help_text=_("category this product belongs to"),
        verbose_name=_("category"),
    )
    brand = ForeignKey(
        "core.Brand",
        on_delete=CASCADE,
        blank=True,
        null=True,
        help_text=_("optionally associate this product with a brand"),
        verbose_name=_("brand"),
    )
    tags = ManyToManyField(
        "core.ProductTag",
        blank=True,
        help_text=_("tags that help describe or group this product"),
        verbose_name=_("product tags"),
    )
    is_digital = BooleanField(
        default=False,
        help_text=_("indicates whether this product is digitally delivered"),
        verbose_name=_("is product digital"),
        blank=False,
        null=False,
    )
    name = CharField(
        max_length=255,
        help_text=_("provide a clear identifying name for the product"),
        verbose_name=_("product name"),
    )
    description = TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text=_("add a detailed description of the product"),
        verbose_name=_("product description"),
    )
    partnumber = CharField(  # noqa: DJ001
        unique=True,
        default=None,
        blank=False,
        null=True,
        help_text=_("part number for this product"),
        verbose_name=_("part number"),
    )
    slug = AutoSlugField(
        populate_from=("uuid", "category__name", "name"),
        allow_unicode=True,
        unique=True,
        editable=False,
        null=True,
    )

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return self.name

    @property
    def rating(self):
        cache_key = f"product_rating_{self.pk}"
        rating = cache.get(cache_key)
        if rating is None:
            feedbacks = Feedback.objects.filter(order_product__product_id=self.pk)
            rating = feedbacks.aggregate(Avg("rating"))["rating__avg"] or 0
            cache.set(cache_key, rating, 604800)
        return round(rating, 2)

    @rating.setter
    def rating(self, value):
        self.__dict__["rating"] = value

    @property
    def feedbacks_count(self):
        cache_key = f"product_feedbacks_count_{self.pk}"
        feedbacks_count = cache.get(cache_key)
        if feedbacks_count is None:
            feedbacks_count = Feedback.objects.filter(order_product__product_id=self.pk).count()
            cache.set(cache_key, feedbacks_count, 604800)
        return feedbacks_count

    @property
    def price(self) -> float:
        stock = self.stocks.order_by("price").only("price").first()
        price = stock.price if stock else 0.0
        return round(price, 2)

    @property
    def quantity(self) -> int:
        cache_key = f"product_quantity_{self.pk}"
        quantity = cache.get(cache_key, 0)
        if not quantity:
            stocks = self.stocks.only("quantity")
            for stock in stocks:
                quantity += stock.quantity
            cache.set(cache_key, quantity, 3600)
        return quantity


class Vendor(NiceModel):
    is_publicly_visible = False

    authentication = JSONField(
        blank=True,
        null=True,
        help_text=_("stores credentials and endpoints required for vendor communication"),
        verbose_name=_("authentication info"),
    )
    markup_percent = IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("define the markup for products retrieved from this vendor"),
        verbose_name=_("vendor markup percentage"),
    )
    name = CharField(
        max_length=255,
        help_text=_("name of this vendor"),
        verbose_name=_("vendor name"),
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("vendor")
        verbose_name_plural = _("vendors")
        indexes = [
            GinIndex(fields=["authentication"]),
        ]


class Feedback(NiceModel):
    is_publicly_visible = True

    comment = TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text=_("user-provided comments about their experience with the product"),
        verbose_name=_("feedback comments"),
    )
    order_product = OneToOneField(
        "core.OrderProduct",
        on_delete=CASCADE,
        blank=False,
        null=False,
        help_text=_("references the specific product in an order that this feedback is about"),
        verbose_name=_("related order product"),
    )
    rating = FloatField(
        blank=True,
        null=True,
        help_text=_("user-assigned rating for the product"),
        verbose_name=_("product rating"),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    def __str__(self) -> str:
        return f"{self.rating} by {self.order_product.order.user.email}"

    class Meta:
        verbose_name = _("feedback")
        verbose_name_plural = _("feedbacks")


class Order(NiceModel):
    is_publicly_visible = False

    billing_address = ForeignKey(
        "geo.Address",
        on_delete=CASCADE,
        blank=True,
        null=True,
        related_name="billing_address_order",
        help_text=_("the billing address used for this order"),
        verbose_name=_("billing address"),
    )
    promo_code = ForeignKey(
        "core.PromoCode",
        on_delete=PROTECT,
        blank=True,
        null=True,
        help_text=_("optional promo code applied to this order"),
        verbose_name=_("applied promo code"),
    )
    shipping_address = ForeignKey(
        "geo.Address",
        on_delete=CASCADE,
        blank=True,
        null=True,
        related_name="shipping_address_order",
        help_text=_("the shipping address used for this order"),
        verbose_name=_("shipping address"),
    )
    status = CharField(
        default="PENDING",
        max_length=64,
        choices=ORDER_STATUS_CHOICES,
        help_text=_("current status of the order in its lifecycle"),
        verbose_name=_("order status"),
    )
    notifications = JSONField(
        blank=True,
        null=True,
        help_text=_("json structure of notifications to display to users"),
        verbose_name=_("notifications"),
    )
    attributes = JSONField(
        blank=True,
        null=True,
        help_text=_("json representation of order attributes for this order"),
        verbose_name=_("attributes"),
    )
    user = ForeignKey(
        "vibes_auth.User",
        on_delete=CASCADE,
        help_text=_("the user who placed the order"),
        verbose_name=_("user"),
        related_name="orders",
        blank=True,
        null=True,
    )
    buy_time = DateTimeField(
        help_text=_("the timestamp when the order was finalized"),
        verbose_name=_("buy time"),
        default=None,
        null=True,
        blank=True,
    )
    human_readable_id = CharField(
        max_length=8,
        help_text=_("a human-readable identifier for the order"),
        verbose_name=_("human readable id"),
        unique=True,
        default=generate_human_readable_id,
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self) -> str:
        return f"{self.pk} Order for {self.user.email}"

    @property
    def is_business(self) -> bool:
        return self.attributes.get("is_business", False) if self.attributes else False

    def save(self, **kwargs):
        if self.user.orders.filter(status="PENDING").count() > 1 and self.status == "PENDING":
            raise ValueError(_("a user must have only one pending order at a time"))
        return super().save(**kwargs)

    @property
    def total_price(self) -> float:
        return (
                round(
                    sum(
                        order_product.buy_price * order_product.quantity
                        if order_product.status not in FAILED_STATUSES and order_product.buy_price is not None
                        else 0.0
                        for order_product in self.order_products.all()
                    ),
                    2,
                )
                or 0.0
        )

    @property
    def total_quantity(self) -> int:
        return sum([op.quantity for op in self.order_products.all()])

    def add_product(self, product_uuid: str | None = None, attributes: list = list):
        if self.status not in ["PENDING", "MOMENTAL"]:
            raise ValueError(_("you cannot add products to an order that is not a pending one"))
        try:
            product = Product.objects.get(uuid=product_uuid)

            if not product.is_active:
                raise BadRequest(_("you cannot add inactive products to order"))

            buy_price = product.price

            promotions = Promotion.objects.filter(is_active=True, products__in=[product]).order_by("discount_percent")

            if promotions.exists():
                buy_price -= round(product.price * (promotions.first().discount_percent / 100), 2)

            order_product, is_created = OrderProduct.objects.get_or_create(
                product=product,
                order=self,
                attributes=json.dumps(attributes),
                defaults={"quantity": 1, "buy_price": product.price},
            )
            if not is_created:
                if product.quantity < order_product.quantity + 1:
                    raise BadRequest(_("you cannot add more products than available in stock"))
                order_product.quantity += 1
                order_product.buy_price = product.price
                order_product.save()

            return self

        except Product.DoesNotExist:
            name = "Product"
            raise Http404(_(f"{name} does not exist: {product_uuid}"))

    def remove_product(self, product_uuid: str | None = None, attributes: dict = dict):
        if self.status != "PENDING":
            raise ValueError(_("you cannot remove products from an order that is not a pending one"))
        try:
            product = Product.objects.get(uuid=product_uuid)
            order_product = self.order_products.get(product=product, order=self)
            if order_product.quantity == 1:
                self.order_products.remove(order_product)
                order_product.delete()
            else:
                order_product.quantity -= 1
                order_product.save()
            return self
        except Product.DoesNotExist:
            name = "Product"
            raise Http404(_(f"{name} does not exist: {product_uuid}"))
        except OrderProduct.DoesNotExist:
            name = "OrderProduct"
            query = f"product: {product_uuid}, order: {self.uuid}, attributes: {attributes}"
            raise Http404(_(f"{name} does not exist with query <{query}>"))

    def remove_all_products(self):
        if self.status != "PENDING":
            raise ValueError(_("you cannot remove products from an order that is not a pending one"))
        for order_product in self.order_products.all():
            self.order_products.remove(order_product)
            order_product.delete()
        return self

    def remove_products_of_a_kind(self, product_uuid: str):
        if self.status != "PENDING":
            raise ValueError(_("you cannot remove products from an order that is not a pending one"))
        try:
            product = Product.objects.get(uuid=product_uuid)
            order_product = self.order_products.get(product=product, order=self)
            self.order_products.remove(order_product)
            order_product.delete()
        except Product.DoesNotExist:
            name = "Product"
            raise Http404(_(f"{name} does not exist: {product_uuid}"))
        return self

    @property
    def is_whole_digital(self):
        return self.order_products.count() == self.order_products.filter(product__is_digital=True).count()

    def apply_promocode(self, promocode_uuid: str):
        try:
            promocode: PromoCode = PromoCode.objects.get(uuid=promocode_uuid)
        except PromoCode.DoesNotExist:
            raise Http404(_("promocode does not exist"))
        return promocode.use(self)

    def buy(
            self, force_balance: bool = False, force_payment: bool = False, promocode_uuid: str | None = None
    ) -> Self | Transaction | None:
        if config.DISABLED_COMMERCE:
            raise DisabledCommerceError(_("you can not buy at this moment, please try again in a few minutes"))

        if (not force_balance and not force_payment) or (force_balance and force_payment):
            raise ValueError(_("invalid force value"))

        if self.total_quantity < 1:
            raise ValueError(_("you cannot purchase an empty order!"))

        force = None

        if force_balance:
            force = "balance"

        if force_payment:
            force = "payment"

        amount = self.apply_promocode(promocode_uuid) if promocode_uuid else self.total_price

        match force:
            case "balance":
                if self.user.payments_balance.amount < amount:
                    raise NotEnoughMoneyError(_("insufficient funds to complete the order"))
                self.status = "CREATED"
                self.buy_time = timezone.now()
                self.order_products.all().update(status="DELIVERING")
                self.save()
                return self
            case "payment":
                return Transaction.objects.create(
                    balance=self.user.payments_balance,
                    amount=amount,
                    currency=CURRENCY_CODE,
                    order=self,
                )

        return self

    def buy_without_registration(self, products: list, promocode_uuid: str, **kwargs) -> Transaction | None:
        if config.DISABLED_COMMERCE:
            raise DisabledCommerceError(_("you can not buy at this moment, please try again in a few minutes"))

        if len(products) < 1:
            raise ValueError(_("you cannot purchase an empty order!"))

        customer_name = kwargs.pop("customer_name")
        customer_email = kwargs.pop("customer_email")
        customer_phone_number = kwargs.pop("customer_phone_number")

        if not all([customer_name, customer_email, customer_phone_number]):
            raise ValueError(
                _(
                    "you cannot buy without registration, please provide the following information:"
                    " customer name, customer email, customer phone number"
                )
            )

        payment_method = kwargs.get("payment_method")

        if payment_method not in cache.get("payment_methods"):
            raise ValueError(_("invalid payment method"))

        billing_customer_address = kwargs.pop("billing_customer_address")
        billing_customer_city = billing_customer_address.pop("customer_city")
        billing_customer_country = billing_customer_address.pop("customer_country")
        billing_customer_postal_code = billing_customer_address.pop("customer_postal_code")
        billing_customer_address_line = billing_customer_address.pop("customer_address_line")

        if not all(
                [
                    billing_customer_city,
                    billing_customer_country,
                    billing_customer_postal_code,
                    billing_customer_address_line,
                ]
        ):
            raise ValueError(_("you cannot create a momental order without providing a billing address"))

        billing_address = Address.objects.get_or_create(
            user=None,
            country=Country.objects.get(code=billing_customer_country),
            region=Region.objects.get(code=billing_customer_city),
            city=City.objects.get(name=billing_customer_city),
            postal_code=PostalCode.objects.get(code=billing_customer_postal_code),
            street=billing_customer_address_line,
        )

        shipping_customer_address = kwargs.pop("shipping_customer_address")
        shipping_customer_city = shipping_customer_address.pop("customer_city")
        shipping_customer_country = shipping_customer_address.pop("customer_country")
        shipping_customer_postal_code = shipping_customer_address.pop("customer_postal_code")
        shipping_customer_address_line = shipping_customer_address.pop("сustomer_address_line")

        if not shipping_customer_address:
            shipping_address = billing_address

        else:
            shipping_address = Address.objects.get_or_create(
                user=None,
                country=Country.objects.get(code=shipping_customer_country),
                region=Region.objects.get(code=shipping_customer_city),
                city=City.objects.get(name=billing_customer_city),
                postal_code=PostalCode.objects.get(code=shipping_customer_postal_code),
                street=shipping_customer_address_line,
            )

        for product_uuid in products:
            self.add_product(product_uuid)

        amount = self.apply_promocode(promocode_uuid) if promocode_uuid else self.total_price

        self.status = "CREATED"
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.attributes.update(
            {
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone_number": customer_phone_number,
                "is_business": kwargs.get("is_business", False),
            }
        )
        self.save()

        return Transaction.objects.create(
            amount=amount,
            currency=CURRENCY_CODE,
            order=self,
            payment_method=kwargs.get("payment_method"),
        )

    def finalize(self):
        if (
                self.order_products.filter(
                    status__in=[
                        "ACCEPTED",
                        "FAILED",
                        "RETURNED",
                        "CANCELED",
                        "FINISHED",
                    ]
                ).count()
                == self.order_products.count()
        ):
            self.status = "FINISHED"
            self.save()


class OrderProduct(NiceModel):
    is_publicly_visible = False

    buy_price = FloatField(
        blank=True,
        null=True,
        help_text=_("the price paid by the customer for this product at purchase time"),
        verbose_name=_("purchase price at order time"),
    )
    comments = TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text=_("internal comments for admins about this ordered product"),
        verbose_name=_("internal comments"),
    )
    notifications = JSONField(
        blank=True,
        null=True,
        help_text=_("json structure of notifications to display to users"),
        verbose_name=_("user notifications"),
    )
    attributes = JSONField(
        blank=True,
        null=True,
        help_text=_("json representation of this item's attributes"),
        verbose_name=_("ordered product attributes"),
    )
    order = ForeignKey(
        "core.Order",
        on_delete=CASCADE,
        help_text=_("reference to the parent order that contains this product"),
        verbose_name=_("parent order"),
        related_name="order_products",
        null=True,
    )
    product = ForeignKey(
        "core.Product",
        on_delete=PROTECT,
        blank=True,
        null=True,
        help_text=_("the specific product associated with this order line"),
        verbose_name=_("associated product"),
    )
    quantity = PositiveIntegerField(
        blank=False,
        null=False,
        default=1,
        help_text=_("quantity of this specific product in the order"),
        verbose_name=_("product quantity"),
    )
    status = CharField(
        max_length=128,
        blank=False,
        null=False,
        choices=ORDER_PRODUCT_STATUS_CHOICES,
        help_text=_("current status of this product in the order"),
        verbose_name=_("product line status"),
        default="PENDING",
    )

    def __str__(self) -> str:
        return f"{self.product.name} for ({self.order.user.email})"

    class Meta:
        verbose_name = _("order product")
        verbose_name_plural = _("order products")
        indexes = [
            GinIndex(fields=["notifications", "attributes"]),
        ]

    def return_balance_back(self):
        self.status = "RETURNED"
        self.save()
        self.order.user.payments_balance.amount += self.buy_price
        self.order.user.payments_balance.save()

    def add_error(self, error=None):
        if self.notifications is not None:
            order_product_errors = self.notifications.get("errors", [])
            if not order_product_errors:
                self.notifications.update(
                    {
                        "errors": [
                            {"detail": error if error else f"Something went wrong with {self.uuid} for some reason..."},
                        ]
                    }
                )
            else:
                order_product_errors.append({"detail": error})
                self.notifications.update({"errors": order_product_errors})
        else:
            self.notifications = {"errors": [{"detail": error}]}
        self.status = "FAILED"
        self.save()
        return self

    @property
    def total_price(self) -> float:
        return round(self.buy_price * self.quantity, 2)

    @property
    def download_url(self) -> str:
        if self.product.is_digital and self.product.stocks.first().digital_asset:
            return self.download.url
        return ""


class ProductTag(NiceModel):
    is_publicly_visible = True

    tag_name = CharField(
        blank=False,
        null=False,
        max_length=255,
        help_text=_("internal tag identifier for the product tag"),
        verbose_name=_("tag name"),
    )
    name = CharField(
        max_length=255,
        help_text=_("user-friendly name for the product tag"),
        verbose_name=_("tag display name"),
        unique=True,
    )

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name = _("product tag")
        verbose_name_plural = _("product tags")


class ProductImage(NiceModel):
    is_publicly_visible = True

    alt = CharField(
        max_length=255,
        help_text=_("provide alternative text for the image for accessibility"),
        verbose_name=_("image alt text"),
    )
    image = ImageField(
        help_text=_("upload the image file for this product"),
        verbose_name=_("product image"),
        upload_to=get_product_uuid_as_path,
    )
    priority = IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("determines the order in which images are displayed"),
        verbose_name=_("display priority"),
    )
    product = ForeignKey(
        "core.Product",
        on_delete=CASCADE,
        help_text=_("the product that this image represents"),
        verbose_name=_("associated product"),
        related_name="images",
    )

    def get_product_uuid_as_path(self, *args):
        return str(self.product.uuid) + "/" + args[0]

    def __str__(self) -> str:
        return self.alt

    class Meta:
        ordering = ("priority",)
        verbose_name = _("product image")
        verbose_name_plural = _("product images")


class PromoCode(NiceModel):
    is_publicly_visible = False

    code = CharField(
        max_length=20,
        unique=True,
        default=get_random_code,
        help_text=_("unique code used by a user to redeem a discount"),
        verbose_name=_("promo code identifier"),
    )
    discount_amount = DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("fixed discount amount applied if percent is not used"),
        verbose_name=_("fixed discount amount"),
    )
    discount_percent = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        blank=True,
        null=True,
        help_text=_("percentage discount applied if fixed amount is not used"),
        verbose_name=_("percentage discount"),
    )
    end_time = DateTimeField(
        blank=True,
        null=True,
        help_text=_("timestamp when the promocode expires"),
        verbose_name=_("end validity time"),
    )
    start_time = DateTimeField(
        blank=True,
        null=True,
        help_text=_("timestamp from which this promocode is valid"),
        verbose_name=_("start validity time"),
    )
    used_on = DateTimeField(
        blank=True,
        null=True,
        help_text=_("timestamp when the promocode was used, blank if not used yet"),
        verbose_name=_("usage timestamp"),
    )
    user = ForeignKey(
        "vibes_auth.User",
        on_delete=CASCADE,
        help_text=_("user assigned to this promocode if applicable"),
        verbose_name=_("assigned user"),
        null=True,
        blank=True,
        related_name="promocodes",
    )

    class Meta:
        verbose_name = _("promo code")
        verbose_name_plural = _("promo codes")

    def save(self, **kwargs):
        if (self.discount_amount is not None and self.discount_percent is not None) or (
                self.discount_amount is None and self.discount_percent is None
        ):
            raise ValidationError(
                _("only one type of discount should be defined (amount or percent), but not both or neither.")
            )
        super().save(**kwargs)

    def __str__(self) -> str:
        return self.code

    @property
    def discount_type(self):
        if self.discount_amount is not None:
            return "amount"
        return "percent"

    def use(self, order: Order) -> float:
        if self.used_on:
            raise ValueError(_("promocode already used"))
        amount = order.total_price
        match self.discount_type:
            case "percent":
                amount -= round(amount * (self.discount_percent / 100), 2)
                order.attributes.update({"promocode": str(self.uuid), "final_price": amount})
                order.save()
            case "amount":
                amount -= round(float(self.discount_amount), 2)
                order.attributes.update({"promocode": str(self.uuid), "final_price": amount})
                order.save()
            case _:
                raise ValueError(_(f"invalid discount type for promocode {self.uuid}"))
        self.used_on = datetime.datetime(datetime.datetime(self.used_on).year, 1, 1)
        self.save()
        return amount


class Promotion(NiceModel):
    is_publicly_visible = True

    discount_percent = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_("percentage discount for the selected products"),
        verbose_name=_("discount percentage"),
    )
    name = CharField(
        max_length=256,
        unique=True,
        help_text=_("provide a unique name for this promotion"),
        verbose_name=_("promotion name"),
    )
    description = TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text=_("add a detailed description of the product"),
        verbose_name=_("promotion description"),
    )
    products = ManyToManyField(
        "core.Product",
        blank=True,
        help_text=_("select which products are included in this promotion"),
        verbose_name=_("included products"),
    )

    class Meta:
        verbose_name = _("promotion")
        verbose_name_plural = _("promotions")

    def __str__(self) -> str:
        if self.name:
            return self.name
        return str(self.id)


class Stock(NiceModel):
    is_publicly_visible = False

    vendor = ForeignKey(
        "core.Vendor",
        on_delete=CASCADE,
        help_text=_("the vendor supplying this product stock"),
        verbose_name=_("associated vendor"),
    )
    price = FloatField(
        default=0.0,
        help_text=_("final price to the customer after markups"),
        verbose_name=_("selling price"),
    )
    product = ForeignKey(
        "core.Product",
        on_delete=CASCADE,
        help_text=_("the product associated with this stock entry"),
        verbose_name=_("associated product"),
        related_name="stocks",
        blank=True,
        null=True,
    )
    purchase_price = FloatField(
        default=0.0,
        help_text=_("the price paid to the vendor for this product"),
        verbose_name=_("vendor purchase price"),
    )
    quantity = IntegerField(
        default=0,
        help_text=_("available quantity of the product in stock"),
        verbose_name=_("quantity in stock"),
    )
    sku = CharField(
        max_length=255,
        help_text=_("vendor-assigned SKU for identifying the product"),
        verbose_name=_("vendor sku"),
    )
    digital_asset = FileField(
        default=None,
        blank=True,
        null=True,
        help_text=_("digital file associated with this stock if applicable"),
        verbose_name=_("digital file"),
        upload_to="downloadables/",
    )

    def __str__(self) -> str:
        return f"{self.vendor.name} - {self.product!s}"

    class Meta:
        verbose_name = _("stock")
        verbose_name_plural = _("stock entries")


class Wishlist(NiceModel):
    is_publicly_visible = False

    products = ManyToManyField(
        "core.Product",
        blank=True,
        help_text=_("products that the user has marked as wanted"),
        verbose_name=_("wishlisted products"),
    )
    user = OneToOneField(
        "vibes_auth.User",
        on_delete=CASCADE,
        blank=True,
        null=True,
        help_text=_("user who owns this wishlist"),
        verbose_name=_("wishlist owner"),
        related_name="user_related_wishlist",
    )

    def __str__(self):
        return f"{self.user.email}'s wishlist"

    class Meta:
        verbose_name = _("wishlist")
        verbose_name_plural = _("wishlists")

    def add_product(self, product_uuid):
        try:
            product = Product.objects.get(uuid=product_uuid)
            if product in self.products.all():
                return self
            self.products.add(product)
        except Product.DoesNotExist:
            name = "Product"
            raise Http404(_(f"{name} does not exist: {product_uuid}"))

        return self

    def remove_product(self, product_uuid):
        try:
            product = Product.objects.get(uuid=product_uuid)
            if product not in self.products.all():
                return self
        except Product.DoesNotExist:
            name = "Product"
            raise Http404(_(f"{name} does not exist: {product_uuid}"))

        return self

    def bulk_add_products(self, product_uuids):
        self.products.add(*Product.objects.filter(uuid__in=product_uuids))

        return self

    def bulk_remove_products(self, product_uuids):
        self.products.remove(*Product.objects.filter(uuid__in=product_uuids))

        return self


class DigitalAssetDownload(NiceModel):
    is_publicly_visible = False

    order_product = OneToOneField(to=OrderProduct, on_delete=CASCADE, related_name="download")
    num_downloads = IntegerField(default=0)

    class Meta:
        verbose_name = _("download")
        verbose_name_plural = _("downloads")

    def __str__(self):
        return f"{self.order_product} - {self.num_downloads}"

    @property
    def url(self):
        if self.order_product.status != "FINISHED":
            raise ValueError(_("you can not download a digital asset for a non-finished order"))

        return f"https://api.{config.BASE_URL}/download/{urlsafe_base64_encode(force_bytes(self.order_product.uuid))}"


class Documentary(NiceModel):
    is_publicly_visible = True

    product = ForeignKey(to=Product, on_delete=CASCADE, related_name="documentaries")
    document = FileField(upload_to=get_product_uuid_as_path)

    class Meta:
        verbose_name = _("documentary")
        verbose_name_plural = _("documentaries")

    def __str__(self):
        return f"{self.product.name} - {self.document.name}"

    def get_product_uuid_as_path(self, *args):
        return str(self.product.uuid) + "/" + args[0]

    @property
    def file_type(self):
        return self.document.name.split(".")[-1] or _("unresolved")
