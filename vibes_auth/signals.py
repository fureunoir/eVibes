from django.db.models.signals import post_save
from django.dispatch import receiver

from vibes_auth.models import User
from vibes_auth.utils.email import send_verification_email_task


@receiver(post_save, sender=User)
def send_verification_email_signal(instance, created, **kwargs):
    if created:
        send_verification_email_task.delay(instance.uuid)
