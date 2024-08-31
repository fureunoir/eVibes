from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Order, Wishlist
from vibes_auth.models import User


@receiver(post_save, sender=User)
def create_order_on_user_creation_signal(instance, created, **kwargs):
    if created:
        Order.objects.create(user=instance, status='PENDING')



@receiver(post_save, sender=User)
def create_wishlist_on_user_creation_signal(instance, created, **kwargs):
    if created:
        Wishlist.objects.create(user=instance)
