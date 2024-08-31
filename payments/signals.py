from django.db.models.signals import post_save
from django.dispatch import receiver

from payments.models import Balance
from vibes_auth.models import User


@receiver(post_save, sender=User)
def create_balance_on_user_creation_signal(instance, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)
