from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from vibes_auth.models import User
from vibes_auth.utils.emailing import send_verification_email_task


@receiver(post_save, sender=User)
def send_verification_email_signal(instance, created, **kwargs):
    if not created:
        return

    send_verification_email_task.delay(instance.pk)


@receiver(pre_save, sender=User)
def send_user_verification_email(instance, **kwargs):
    if not instance.pk:
        return

    try:
        old = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    if old.email != instance.email:
        instance.is_active = False
        transaction.on_commit(
            lambda: send_verification_email_task.delay(instance.pk)
        )
