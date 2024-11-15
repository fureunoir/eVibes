from datetime import datetime

from celery.app import shared_task
from constance import config
from django.utils.translation import activate

from core.models import Order
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from core.utils.constance import set_email_settings


@shared_task
def contact_us_email(contact_info):
    set_email_settings()

    email = EmailMessage(
        f'{config.PROJECT_NAME} | Contact Us initiated', render_to_string('contact_us_email.html', {
            'email': contact_info.get('email'),
            'name': contact_info.get('name'),
            'subject': contact_info.get('subject', 'Without subject'),
            'phone_number': contact_info.get('phone_number', 'Without phone number'),
            'message': contact_info.get('message'),
            'current_year': timezone.now().year,
            'config': config
        }), to=[config.EMAIL_HOST_USER],
        from_email=config.EMAIL_HOST_USER,
    )
    email.content_subtype = "html"
    email.send()

@shared_task
def send_order_created_email(order_pk: str) -> tuple[bool, str]:
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return False, f'Order not found with the given pk: {order_pk}'

    activate(order.user.language)

    set_email_settings()

    email = EmailMessage(
        f'{config.PROJECT_NAME} | Order Confirmation', render_to_string('order_created_email.html', {
            'order': order,
            'today': datetime.today(),
            'config': config,
            'total_price': order.total_price + 5.0
        }), to=[order.user.email],
        from_email=config.EMAIL_HOST_USER,
    )
    email.content_subtype = "html"
    email.send()

    return True, order.uuid