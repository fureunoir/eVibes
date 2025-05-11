import logging
from datetime import timedelta

from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from sentry_sdk import capture_exception

from core.models import Category, Order, Product, PromoCode, Wishlist
from core.utils import generate_human_readable_id, resolve_translations_for_elasticsearch
from core.utils.emailing import send_order_created_email, send_order_finished_email
from evibes.utils.misc import create_object
from vibes_auth.models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_order_on_user_creation_signal(instance, created, **kwargs):
    if created:
        try:
            Order.objects.create(user=instance, status="PENDING")
        except IntegrityError:
            human_readable_id = generate_human_readable_id()
            while True:
                if Order.objects.filter(human_readable_id=human_readable_id).exists():
                    human_readable_id = generate_human_readable_id()
                    continue
                Order.objects.create(user=instance, status="PENDING", human_readable_id=human_readable_id)
                break


@receiver(post_save, sender=User)
def create_wishlist_on_user_creation_signal(instance, created, **kwargs):
    if created:
        Wishlist.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_promocode_on_user_referring(instance, created, **kwargs):
    try:
        if created and instance.attributes.get("referrer", ""):
            referrer_uuid = urlsafe_base64_decode(instance.attributes.get("referrer", ""))
            referrer = User.objects.get(uuid=referrer_uuid)
            code = f"WELCOME-{get_random_string(6)}"
            PromoCode.objects.create(
                user=referrer,
                code=code if len(code) <= 20 else code[:20],
                discount_percent=10,
                start_time=now(),
                end_time=now() + timedelta(days=30),
            )
    except Exception as e:
        capture_exception(e)
        logger.error(_(f"error during promocode creation: {e!s}"))


@receiver(post_save, sender=Order)
def process_order_changes(instance, created, **kwargs):
    if not created:
        if instance.status != "PENDING" and instance.user:
            pending_orders = Order.objects.filter(user=instance.user, status="PENDING")

            if not pending_orders.exists():
                try:
                    Order.objects.create(user=instance.user, status="PENDING")
                except IntegrityError:
                    human_readable_id = generate_human_readable_id()
                    while True:
                        if Order.objects.filter(human_readable_id=human_readable_id).exists():
                            human_readable_id = generate_human_readable_id()
                            continue
                        Order.objects.create(user=instance, status="PENDING", human_readable_id=human_readable_id)
                        break

        if instance.status == "CREATED":
            if not instance.is_whole_digital:
                send_order_created_email.delay(instance.uuid)

            for order_product in instance.order_products.filter(status="DELIVERING"):
                if not order_product.product.is_digital:
                    continue

                try:
                    vendor_name = (
                        order_product.product.stocks.filter(price=order_product.buy_price).first().vendor.name.lower()
                    )

                    vendor = create_object(f"core.vendors.{vendor_name}", f"{vendor_name.title()}Vendor")

                    vendor.buy_order_product(order_product)

                except Exception as e:
                    order_product.add_error(f"Failed to buy {order_product.uuid}. Reason: {e}...")

            else:
                instance.finalize()

            if instance.order_products.filter(status="FAILED").count() == instance.order_products.count():
                instance.status = "FAILED"
                instance.save()

        if instance.status == "FINISHED":
            send_order_finished_email.delay(instance.uuid)


@receiver(post_save, sender=Product)
def update_product_name_lang(instance, created, **kwargs):
    resolve_translations_for_elasticsearch(instance, "name")
    resolve_translations_for_elasticsearch(instance, "description")


@receiver(post_save, sender=Category)
def update_category_name_lang(instance, created, **kwargs):
    resolve_translations_for_elasticsearch(instance, "name")
    resolve_translations_for_elasticsearch(instance, "description")
