from celery.app import shared_task
from constance import config
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _

from core.utils.constance import set_email_settings
from vibes_auth.models import User


@shared_task
def send_verification_email_task(user_pk: str) -> tuple[bool, str]:
    try:
        user = User.objects.get(pk=user_pk)
        user.refresh_from_db()

        activate(user.language)

        set_email_settings()
        connection = mail.get_connection()

        email_subject = _(f"{config.PROJECT_NAME} | Activate Account")
        email_body = render_to_string(
            "user_verification_email.html",
            {
                "user_first_name": user.first_name,
                "activation_link": f"https://{config.FRONTEND_DOMAIN}/{user.language}/activate-user?uid={urlsafe_base64_encode(force_bytes(user.uuid))}"
                f"&token={urlsafe_base64_encode(force_bytes(user.activation_token))}",
                "project_name": config.PROJECT_NAME,
            },
        )

        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=f"{config.PROJECT_NAME} <{config.EMAIL_FROM}>",
            to=[user.email],
            connection=connection,
        )
        email.content_subtype = "html"
        email.send()

    except User.DoesNotExist:
        return False, _(f"user not found with the given pk: {user_pk}")

    except Exception as e:
        return False, _(f"something went wrong while sending an email: {e!s}")

    else:
        return True, user.uuid


@shared_task
def send_reset_password_email_task(user_pk: str) -> tuple[bool, str]:
    try:
        user = User.objects.get(pk=user_pk)
        user.refresh_from_db()

        activate(user.language)

        set_email_settings()
        connection = mail.get_connection()

        email_subject = _(f"{config.PROJECT_NAME} | Reset Password")
        email_body = render_to_string(
            "user_reset_password_email.html",
            {
                "user_first_name": user.first_name,
                "reset_link": f"https://{config.FRONTEND_DOMAIN}/{user.language}/reset-password?uid="
                f"{urlsafe_base64_encode(force_bytes(user.pk))}"
                f"&token={PasswordResetTokenGenerator().make_token(user)}",
                "project_name": config.PROJECT_NAME,
            },
        )

        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=f"{config.PROJECT_NAME} <{config.EMAIL_FROM}>",
            to=[user.email],
            connection=connection,
        )
        email.content_subtype = "html"
        email.send()

    except User.DoesNotExist:
        return False, _(f"user not found with the given pk: {user_pk}")

    except Exception as e:
        return False, _(f"something went wrong while sending an email: {e!s}")

    else:
        return True, user.uuid
