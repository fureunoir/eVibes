from constance import config
from django.contrib.postgres.indexes import GinIndex
from django.db.models import CASCADE, CharField, FloatField, ForeignKey, JSONField, OneToOneField
from django.utils.translation import gettext_lazy as _

from core.abstract import NiceModel


class Balance(NiceModel):
    amount = FloatField(null=False, blank=False, default=0)
    user = OneToOneField(
        to="vibes_auth.User", on_delete=CASCADE, blank=True, null=True, related_name="payments_balance"
    )

    def __str__(self):
        return f"{self.user.email} | {self.amount}"

    class Meta:
        verbose_name = _("balance")
        verbose_name_plural = _("balances")

    def save(self, **kwargs):
        if self.amount != 0.0 and len(str(self.amount).split(".")[1]) > 2:
            self.amount = round(self.amount, 2)
        super().save(**kwargs)


class Transaction(NiceModel):
    amount = FloatField(null=False, blank=False)
    balance = ForeignKey(Balance, on_delete=CASCADE, blank=True, null=True, related_name="transactions")
    currency = CharField(max_length=3, null=False, blank=False)
    payment_method = CharField(max_length=20, null=True, blank=True)  # noqa: DJ001
    order = ForeignKey(
        "core.Order",
        on_delete=CASCADE,
        blank=True,
        null=True,
        help_text=_("order to process after paid"),
        related_name="payments_transactions",
    )
    process = JSONField(verbose_name=_("processing details"), default=dict)

    def __str__(self):
        return f"{self.balance.user.email} | {self.amount}"

    def save(self, **kwargs):
        if self.amount != 0.0 and (
                (config.PAYMENT_GATEWAY_MINIMUM <= self.amount <= config.PAYMENT_GATEWAY_MAXIMUM)
                or (config.PAYMENT_GATEWAY_MINIMUM == 0 and config.PAYMENT_GATEWAY_MAXIMUM == 0)
        ):
            if len(str(self.amount).split(".")[1]) > 2:
                self.amount = round(self.amount, 2)
            super().save(**kwargs)
            return self
        raise ValueError(
            _(f"transaction amount must fit into {config.PAYMENT_GATEWAY_MINIMUM}-{config.PAYMENT_GATEWAY_MAXIMUM}")
        )

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
        indexes = [
            GinIndex(fields=["process"]),
        ]
