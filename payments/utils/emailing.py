from celery.app import shared_task
from constance import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import activate

from vibes_auth.models import User


@shared_task
def balance_email(user_pk: str) -> tuple[bool, str]:
    pass
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return False, f"Order not found with the given pk: {user_pk}"

    activate(user.language)

    email = EmailMessage(
        "eVibes | Successful Order",
        render_to_string("balance.html", {"user": user, "current_year": timezone.now().year, "config": config}),
        to=[user.email],
        from_email=f"{config.PROJECT_NAME} <{config.EMAIL_FROM}>",
    )
    email.content_subtype = "html"
    email.send()

    return True, user.uuid
