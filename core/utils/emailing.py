from datetime import datetime

from celery.app import shared_task
from constance import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _

from core.models import Order, OrderProduct
from core.utils.constance import set_email_settings


@shared_task
def contact_us_email(contact_info):
    set_email_settings()

    email = EmailMessage(
        _(f"{config.PROJECT_NAME} | contact us initiated"),
        render_to_string(
            "contact_us_email.html",
            {
                "email": contact_info.get("email"),
                "name": contact_info.get("name"),
                "subject": contact_info.get("subject", "Without subject"),
                "phone_number": contact_info.get("phone_number", "Without phone number"),
                "message": contact_info.get("message"),
                "config": config,
            },
        ),
        to=[config.EMAIL_HOST_USER],
        from_email=f"{config.PROJECT_NAME} <{config.EMAIL_FROM}>",
    )
    email.content_subtype = "html"
    email.send()

    return True, str(contact_info.get("email"))


@shared_task
def send_order_created_email(order_pk: str) -> tuple[bool, str]:
    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return False, f"Order not found with the given pk: {order_pk}"

    activate(order.user.language)

    set_email_settings()

    if not order.is_whole_digital:
        email = EmailMessage(
            _(f"{config.PROJECT_NAME} | order confirmation"),
            render_to_string(
                "digital_order_created_email.html" if order.is_whole_digital else "shipped_order_created_email.html",
                {
                    "order": order,
                    "today": datetime.today(),
                    "config": config,
                    "total_price": order.total_price,
                },
            ),
            to=[order.user.email],
            from_email=f"{config.PROJECT_NAME} <{config.EMAIL_FROM}>",
        )
        email.content_subtype = "html"
        email.send()

    return True, str(order.uuid)


@shared_task
def send_order_finished_email(order_pk: str) -> tuple[bool, str]:
    def send_digital_assets_email(ops: list[OrderProduct]):
        if len(ops) <= 0:
            return

        activate(order.user.language)

        set_email_settings()

        email = EmailMessage(
            _(f"{config.PROJECT_NAME} | order delivered"),
            render_to_string(
                template_name="digital_order_delivered_email.html",
                context={
                    "order_uuid": order.uuid,
                    "user_first_name": order.user.first_name,
                    "order_products": ops,
                    "project_name": config.PROJECT_NAME,
                    "contact_email": config.EMAIL_FROM,
                    "total_price": round(sum(op.buy_price for op in ops), 2),
                    "display_system_attributes": order.user.has_perm("core.view_order"),
                    "today": datetime.today(),
                },
            ),
            to=[order.user.email],
            from_email=f"{config.PROJECT_NAME} <{config.EMAIL_FROM}>",
        )
        email.content_subtype = "html"
        email.send()

    def send_thank_you_email(ops: list[OrderProduct]):
        activate(order.user.language)

        set_email_settings()

        pass

    try:
        order = Order.objects.get(pk=order_pk)
    except Order.DoesNotExist:
        return False, f"Order not found with the given pk: {order_pk}"

    digital_ops = []

    for digital_op in order.order_products.filter(
        product__is_digital=True,
        status__in=[
            "FINISHED",
            "DELIVERED",
            "ACCEPTED",
        ],
    ):
        digital_ops.append(digital_op)

    send_digital_assets_email(digital_ops)

    shipped_ops = []

    for shipped_op in order.order_products.filter(
        product__is_digital=False,
        status__in=[
            "FINISHED",
            "DELIVERED",
            "ACCEPTED",
        ],
    ):
        shipped_ops.append(shipped_op)

    send_thank_you_email(shipped_ops)

    return True, str(order.uuid)
