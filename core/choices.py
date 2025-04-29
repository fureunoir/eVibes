from django.utils.translation import gettext_lazy as _

ORDER_PRODUCT_STATUS_CHOICES = (
    ("FINISHED", _("finished")),
    ("DELIVERING", _("delivering")),
    ("DELIVERED", _("delivered")),
    ("CANCELED", _("canceled")),
    ("FAILED", _("failed")),
    ("PENDING", _("pending")),
    ("ACCEPTED", _("accepted")),
    ("RETURNED", _("money returned")),
)

ORDER_STATUS_CHOICES = (
    ("PENDING", _("pending")),
    ("FAILED", _("failed")),
    ("PAYMENT", _("payment")),
    ("CREATED", _("created")),
    ("DELIVERING", _("delivering")),
    ("FINISHED", _("finished")),
    ("MOMENTAL", _("momental")),
)

TRANSACTION_STATUS_CHOICES = (("failed", _("failed")), ("successful", _("successful")))
