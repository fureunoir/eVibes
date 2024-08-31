from celery.app import shared_task
from constance import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone


@shared_task
def contact_us_email(contact_info):
    email = EmailMessage(
        'eVibes | Contact Us initiated', render_to_string('contact_us_email.html', {
            'email': contact_info.get('email'),
            'name': contact_info.get('name'),
            'subject': contact_info.get('subject', 'Without subject'),
            'phone_number': contact_info.get('phone_number', 'Without phone number'),
            'message': contact_info.get('message'),
            'current_year': timezone.now().year,
            'config': config
        }), to=[config.EMAIL_HOST_USER],
    )
    email.content_subtype = "html"
    email.send()
