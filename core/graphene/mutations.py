import logging

import requests
from django.core.cache import cache
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from graphene import UUID, Boolean, Field, Int, List, String
from graphene.types.generic import GenericScalar
from graphene_django.utils import camelize

from core.elasticsearch import process_query
from core.graphene import BaseMutation
from core.graphene.object_types import OrderType, ProductType, SearchResultsType, WishlistType
from core.models import Category, Order, Product, Wishlist
from core.utils import format_attributes, is_url_safe
from core.utils.caching import web_cache
from core.utils.emailing import contact_us_email
from core.utils.messages import permission_denied_message
from geo.graphene.object_types import UnregisteredCustomerAddressInput
from payments.graphene.object_types import TransactionType

logger = logging.getLogger(__name__)


class CacheOperator(BaseMutation):
    class Meta:
        description = _("cache I/O")

    class Arguments:
        key = String(required=True, description=_("key to look for in or set into the cache"))
        data = GenericScalar(required=False, description=_("data to store in cache"))
        timeout = Int(
            required=False,
            description=_("timeout in seconds to set the data for into the cache"),
        )

    data = GenericScalar(description=_("cached data"))

    @staticmethod
    def mutate(_parent, info, key, data=None, timeout=None):
        return camelize(web_cache(info.context, key, data, timeout))


class RequestCursedURL(BaseMutation):
    class Meta:
        description = _("request a CORSed URL")

    class Arguments:
        url = String(required=True)

    data = GenericScalar(description=_("camelized JSON data from the requested URL"))

    @staticmethod
    def mutate(_parent, info, url):
        if not is_url_safe(url):
            raise BadRequest(_("only URLs starting with http(s):// are allowed"))
        try:
            data = cache.get(url, None)
            if not data:
                response = requests.get(url, headers={"content-type": "application/json"})
                response.raise_for_status()
                data = camelize(response.json())
                cache.set(url, data, 86400)
            return {"data": data}
        except Exception as e:
            return {"data": {"error": str(e)}}


class AddOrderProduct(BaseMutation):
    class Meta:
        description = _("add a product to the order")

    class Arguments:
        product_uuid = UUID(required=True)
        order_uuid = UUID(required=True)
        attributes = String(required=False)

    order = Field(OrderType)

    @staticmethod
    def mutate(_parent, info, product_uuid, order_uuid, attributes=None):
        user = info.context.user
        try:
            order = Order.objects.get(uuid=order_uuid)
            if not (user.has_perm("core.add_orderproduct") or user == order.user):
                raise PermissionDenied(permission_denied_message)

            order = order.add_product(product_uuid=product_uuid, attributes=format_attributes(attributes))

            return AddOrderProduct(order=order)
        except Order.DoesNotExist:
            raise Http404(_(f"order {order_uuid} not found"))


class RemoveOrderProduct(BaseMutation):
    class Meta:
        description = _("remove a product from the order")

    class Arguments:
        product_uuid = UUID(required=True)
        order_uuid = UUID(required=True)
        attributes = String(required=False)

    order = Field(OrderType)

    @staticmethod
    def mutate(_parent, info, product_uuid, order_uuid, attributes=None):
        user = info.context.user
        try:
            order = Order.objects.get(uuid=order_uuid)
            if not (user.has_perm("core.change_orderproduct") or user == order.user):
                raise PermissionDenied(permission_denied_message)

            order = order.remove_product(product_uuid=product_uuid, attributes=format_attributes(attributes))

            return AddOrderProduct(order=order)
        except Order.DoesNotExist:
            raise Http404(_(f"order {order_uuid} not found"))


class RemoveAllOrderProducts(BaseMutation):
    class Meta:
        description = _("remove all products from the order")

    class Arguments:
        order_uuid = UUID(required=True)

    order = Field(OrderType)

    @staticmethod
    def mutate(_parent, info, order_uuid):
        user = info.context.user
        order = Order.objects.get(uuid=order_uuid)
        if not (user.has_perm("core.delete_orderproduct") or user == order.user):
            raise PermissionDenied(permission_denied_message)

        order = order.remove_all_products()

        return RemoveAllOrderProducts(order=order)


class RemoveOrderProductsOfAKind(BaseMutation):
    class Meta:
        description = _("remove a product from the order")

    class Arguments:
        product_uuid = UUID(required=True)
        order_uuid = UUID(required=True)

    order = Field(OrderType)

    @staticmethod
    def mutate(_parent, info, product_uuid, order_uuid):
        user = info.context.user
        order = Order.objects.get(uuid=order_uuid)
        if not (user.has_perm("core.delete_orderproduct") or user == order.user):
            raise PermissionDenied(permission_denied_message)

        order = order.remove_products_of_a_kind(product_uuid=product_uuid)

        return RemoveOrderProductsOfAKind(order=order)


class BuyOrder(BaseMutation):
    class Meta:
        description = _("buy an order")

    class Arguments:
        order_uuid = UUID(required=False)
        order_hr_id = String(required=False)
        force_balance = Boolean(required=False)
        force_payment = Boolean(required=False)
        promocode_uuid = UUID(required=False)

    order = Field(OrderType, required=False)
    transaction = Field(TransactionType, required=False)

    @staticmethod
    def mutate(_parent, info, order_uuid=None, order_hr_id=None, force_balance=False, force_payment=False,
               promocode_uuid=None):
        if not any([order_uuid, order_hr_id]) or all([order_uuid, order_hr_id]):
            raise BadRequest(_("please provide either order_uuid or order_hr_id - mutually exclusive"))
        user = info.context.user
        try:

            if order_uuid:
                order = Order.objects.get(user=user, uuid=order_uuid)
            if order_hr_id:
                order = Order.objects.get(user=user, human_readable_id=order_hr_id)

            instance = order.buy(
                force_balance=force_balance, force_payment=force_payment, promocode_uuid=promocode_uuid
            )
            match str(type(instance)):
                case "<class 'payments.models.Transaction'>":
                    return BuyOrder(transaction=instance)
                case "<class 'core.models.Order'>":
                    return BuyOrder(order=instance)
                case _:
                    raise TypeError(_(f"wrong type came from order.buy() method: {type(instance)!s}"))
        except Order.DoesNotExist:
            raise Http404(_(f"order {order_uuid} not found"))


class BuyUnregisteredOrder(BaseMutation):
    class Meta:
        description = _("purchase an order without account creation")

    class Arguments:
        products = List(UUID, required=True)
        promocode_uuid = UUID(required=False)
        customer_name = String(required=True)
        customer_email = String(required=True)
        customer_phone = String(required=True)
        customer_billing_address = UnregisteredCustomerAddressInput(required=True)
        customer_shipping_address = UnregisteredCustomerAddressInput(required=False)
        payment_method = String(required=True)

    transaction = Field(TransactionType, required=False)

    @staticmethod
    def mutate(_parent, info, products, customer_name, customer_email, customer_phone, customer_billing_address,
               payment_method, customer_shipping_address=None, promocode_uuid=None):
        order = Order.objects.create(status="MOMENTAL")
        transaction = order.buy_without_registration(products=products,
                                                     promocode_uuid=promocode_uuid,
                                                     customer_name=customer_name,
                                                     customer_email=customer_email,
                                                     customer_phone=customer_phone,
                                                     customer_billing_address=customer_billing_address,
                                                     customer_shipping_address=customer_shipping_address,
                                                     payment_method=payment_method)
        return BuyUnregisteredOrder(transaction=transaction)


class AddWishlistProduct(BaseMutation):
    class Meta:
        description = _("add a product to the wishlist")

    class Arguments:
        product_uuid = UUID(required=True)
        wishlist_uuid = UUID(required=True)

    wishlist = Field(WishlistType)

    @staticmethod
    def mutate(_parent, info, product_uuid, wishlist_uuid):
        user = info.context.user
        try:
            wishlist = Wishlist.objects.get(uuid=wishlist_uuid)

            if not (user.has_perm("core.change_wishlist") or user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            wishlist.add_product(product_uuid=product_uuid)

            return AddWishlistProduct(wishlist=wishlist)

        except Wishlist.DoesNotExist:
            raise Http404(_(f"wishlist {wishlist_uuid} not found"))


class RemoveWishlistProduct(BaseMutation):
    class Meta:
        description = _("remove a product from the wishlist")

    class Arguments:
        product_uuid = UUID(required=True)
        wishlist_uuid = UUID(required=True)

    wishlist = Field(WishlistType)

    @staticmethod
    def mutate(_parent, info, product_uuid, wishlist_uuid):
        user = info.context.user
        try:
            wishlist = Wishlist.objects.get(uuid=wishlist_uuid)

            if not (user.has_perm("core.change_wishlist") or user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            wishlist.remove_product(product_uuid=product_uuid)

            return RemoveWishlistProduct(wishlist=wishlist)

        except Wishlist.DoesNotExist:
            raise Http404(_(f"wishlist {wishlist_uuid} not found"))


class RemoveAllWishlistProducts(BaseMutation):
    class Meta:
        description = _("remove all products from the wishlist")

    class Arguments:
        wishlist_uuid = UUID(required=True)

    wishlist = Field(WishlistType)

    @staticmethod
    def mutate(_parent, info, wishlist_uuid):
        user = info.context.user
        try:
            wishlist = Wishlist.objects.get(uuid=wishlist_uuid)

            if not (user.has_perm("core.change_wishlist") or user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            for product in wishlist.products.all():
                wishlist.remove_product(product_uuid=product.pk)

            return RemoveAllWishlistProducts(wishlist=wishlist)

        except Wishlist.DoesNotExist:
            raise Http404(_(f"wishlist {wishlist_uuid} not found"))


class BuyWishlist(BaseMutation):
    class Meta:
        description = _("buy all products from the wishlist")

    class Arguments:
        wishlist_uuid = UUID(required=True)
        force_balance = Boolean(required=False)
        force_payment = Boolean(required=False)

    order = Field(OrderType, required=False)
    transaction = Field(TransactionType, required=False)

    @staticmethod
    def mutate(_parent, info, wishlist_uuid, force_balance=False, force_payment=False):
        user = info.context.user
        try:
            wishlist = Wishlist.objects.get(uuid=wishlist_uuid)

            if not (user.has_perm("core.change_wishlist") or user == wishlist.user):
                raise PermissionDenied(permission_denied_message)

            order = Order.objects.create(user=user, status="MOMENTAL")

            for product in (
                    wishlist.products.all()
                    if user.has_perm("core.change_wishlist")
                    else wishlist.products.filter(is_active=True)
            ):
                order.add_product(product_uuid=product.pk)

            instance = order.buy(force_balance=force_balance, force_payment=force_payment)
            match str(type(instance)):
                case "<class 'payments.models.Transaction'>":
                    return BuyWishlist(transaction=instance)
                case "<class 'core.models.Order'>":
                    return BuyWishlist(order=instance)
                case _:
                    raise TypeError(_(f"wrong type came from order.buy() method: {type(instance)!s}"))

        except Wishlist.DoesNotExist:
            raise Http404(_(f"wishlist {wishlist_uuid} not found"))


class BuyProduct(BaseMutation):
    class Meta:
        description = _("buy a product")

    class Arguments:
        product_uuid = UUID(required=True)
        attributes = String(
            required=False,
            description=_("please send the attributes as the string formatted like attr1=value1,attr2=value2"),
        )
        force_balance = Boolean(required=False)
        force_payment = Boolean(required=False)

    order = Field(OrderType, required=False)
    transaction = Field(TransactionType, required=False)

    @staticmethod
    def mutate(_parent, info, product_uuid, attributes=None, force_balance=False, force_payment=False):
        user = info.context.user
        order = Order.objects.create(user=user, status="MOMENTAL")
        order.add_product(product_uuid=product_uuid, attributes=format_attributes(attributes))
        instance = order.buy(force_balance=force_balance, force_payment=force_payment)
        match str(type(instance)):
            case "<class 'payments.models.Transaction'>":
                return BuyProduct(transaction=instance)
            case "<class 'core.models.Order'>":
                return BuyProduct(order=instance)
            case _:
                raise TypeError(_(f"wrong type came from order.buy() method: {type(instance)!s}"))


class CreateProduct(BaseMutation):
    class Arguments:
        name = String(required=True)
        description = String()
        category_uuid = UUID(required=True)

    product = Field(ProductType)

    @staticmethod
    def mutate(_parent, info, name, category_uuid, description=None):
        if not info.context.user.has_perm("core.add_product"):
            raise PermissionDenied(permission_denied_message)
        category = Category.objects.get(uuid=category_uuid)
        product = Product.objects.create(name=name, description=description, category=category)
        return CreateProduct(product=product)


class UpdateProduct(BaseMutation):
    class Arguments:
        uuid = UUID(required=True)
        name = String()
        description = String()
        category_uuid = UUID()

    product = Field(ProductType)

    @staticmethod
    def mutate(_parent, info, uuid, name=None, description=None, category_uuid=None):
        user = info.context.user
        if not user.has_perm("core.change_product"):
            raise PermissionDenied(permission_denied_message)
        product = Product.objects.get(uuid=uuid)
        if name:
            product.name = name
        if description:
            product.description = description
        if category_uuid:
            product.category = Category.objects.get(uuid=category_uuid)
        product.save()
        return UpdateProduct(product=product)


class DeleteProduct(BaseMutation):
    class Arguments:
        uuid = UUID(required=True)

    ok = Boolean()

    @staticmethod
    def mutate(_parent, info, uuid):
        user = info.context.user
        if not user.has_perm("core.delete_product"):
            raise PermissionDenied(permission_denied_message)
        product = Product.objects.get(uuid=uuid)
        product.delete()
        return DeleteProduct(ok=True)


class ContactUs(BaseMutation):
    class Arguments:
        email = String(required=True)
        name = String(required=True)
        subject = String(required=True)
        phone_number = String(required=False)
        message = String(required=True)

    received = Boolean(required=True)
    error = String()

    @staticmethod
    def mutate(_parent, info, email, name, subject, message, phone_number=None):
        try:
            contact_us_email.delay(
                {
                    "email": email,
                    "name": name,
                    "subject": subject,
                    "phone_number": phone_number,
                    "message": message,
                }
            )
            return ContactUs(received=True)
        except Exception as e:
            return ContactUs(received=False, error=str(e))


class Search(BaseMutation):
    class Arguments:
        query = String(required=True)

    results = Field(SearchResultsType)

    class Meta:
        description = _("elasticsearch - works like a charm")

    @staticmethod
    def mutate(_parent, info, query):
        data = process_query(query)

        return Search(
            results=SearchResultsType(
                products=data["products"],
                categories=data["categories"],
                brands=data["brands"],
                posts=data["posts"],
            )
        )
