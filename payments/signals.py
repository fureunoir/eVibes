from django.db.models.signals import post_save
from django.dispatch import receiver

from payments.models import Balance, Transaction
from vibes_auth.models import User


@receiver(post_save, sender=User)
def create_balance_on_user_creation_signal(instance, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)


@receiver(post_save, sender=Transaction)
def process_transaction_changes(instance, created, **kwargs):
    if created:
        try:
            gateway = object()
            gateway.process_transaction(instance)
        except Exception: # noqa:
            instance.process = {"status": "NOGATEWAY"}
