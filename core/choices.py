from django.utils.translation import gettext_lazy as _

ORDER_PRODUCT_STATUS_CHOICES = (
    ('FINISHED', _('finished')),
    ('DELIVERING', _('delivering')),
    ('DELIVERED', _('delivered')),
    ('CANCELED', _('canceled')),
    ('FAILED', _('failed')),
    ('PENDING', _('pending')),
    ('ACCEPTED', _('accepted')),
)

ORDER_STATUS_CHOICES = (
    ('PENDING', _('pending')),
    ('FAILED', _('failed')),
    ('PAYMENT', _('payment')),
    ('FINISHED', _('finished')),
)

TRANSACTION_TYPE_CHOICES = (
    ('TOP', _('top-up')),
    ('DOWN', _('decreasing'))
)

TRANSACTION_STATUS_CHOICES = (
    ('failed', _('failed')),
    ('successful', _('successful'))
)