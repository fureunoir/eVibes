from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Order, Wishlist
from core.utils.email import send_order_created_email
from vibes_auth.models import User


@receiver(post_save, sender=User)
def create_order_on_user_creation_signal(instance, created, **kwargs):
    if created:
        Order.objects.create(user=instance, status='PENDING')


@receiver(post_save, sender=User)
def create_wishlist_on_user_creation_signal(instance, created, **kwargs):
    if created:
        Wishlist.objects.create(user=instance)


@receiver(post_save, sender=Order)
def process_order_changes(instance, created, **kwargs):
    if not created:
        if instance.status != 'PENDING':
            pending_orders = Order.objects.filter(user=instance.user, status='PENDING')

            if not pending_orders.exists():
                Order.objects.create(user=instance.user, status='PENDING')

        if instance.status == 'CREATED':
            send_order_created_email.delay(instance.uuid)
