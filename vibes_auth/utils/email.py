from celery.app import shared_task
from constance import config
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import activate, gettext_lazy as _

from core.utils.constance import set_email_settings
from vibes_auth.models import User


@shared_task
def send_verification_email_task(user_pk: str) -> tuple[bool, str]:
    try:
        user = User.objects.get(pk=user_pk)

        activate(user.language)

        set_email_settings()

        email_subject = _(f'{config.PROJECT_NAME} | Activate Your Account')
        email_body = render_to_string('user_verification_email.html', {
            'user': user,
            'activation_link': f"https://{config.FRONTEND_DOMAIN}?uid={urlsafe_base64_encode(force_bytes(user.uuid))}&token={urlsafe_base64_encode(force_bytes(user.activation_token))}",
            'current_year': timezone.now().year,
            'config': config
        })

        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=config.EMAIL_HOST_USER,
            to=[user.email]
        )
        email.content_subtype = "html"
        email.send()

    except Exception as e:
        return False, f"Something went wrong while sending an email: {str(e)}"

    except User.DoesNotExist:
        return False, f'User not found with the given pk: {user_pk}'

    else:
        return True, user.uuid


@shared_task
def send_reset_password_email_task(user_pk: str, domain: str) -> tuple[bool, str]:
    try:
        user = User.objects.get(pk=user_pk)

        activate(user.language)

        set_email_settings()

        email_subject = _(f'{config.PROJECT_NAME} | Reset Your Password')
        email_body = render_to_string('user_reset_password_email.html', {
            'user': user,
            'reset_link': f"https://{config.FRONTEND_DOMAIN}?uid={urlsafe_base64_encode(force_bytes(user.pk))}&token={PasswordResetTokenGenerator().make_token(user)}",
            'current_year': timezone.now().year,
            'config': config
        })

        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=config.EMAIL_HOST_USER,
            to=[user.email]
        )
        email.content_subtype = "html"
        email.send()

    except User.DoesNotExist:
        return False, f'User not found with the given pk: {user_pk}'

    except Exception as e:
        return False, f"Something went wrong while sending an email: {str(e)}"

    else:
        return True, user.uuid
