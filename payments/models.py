from django.contrib.postgres.indexes import GinIndex
from django.db.models import FloatField, OneToOneField, ForeignKey, CASCADE, CharField, JSONField
from django.utils.translation import gettext_lazy as _

from core.abstract import NiceModel
from payments.managers import TransactionManager


class Balance(NiceModel):
    amount = FloatField(null=False, blank=False, default=0)
    user = OneToOneField(to='vibes_auth.User', on_delete=CASCADE, blank=False, null=False,
                         related_name='payments_balance')

    def __str__(self):
        return f"{self.user.email} | {self.amount}"

    class Meta:
        verbose_name = _('Balance')
        verbose_name_plural = _('Balances')


class Transaction(NiceModel):
    amount = FloatField(null=False, blank=False)
    balance = ForeignKey(Balance, on_delete=CASCADE, blank=False, null=False)
    currency = CharField(max_length=3, null=False, blank=False)
    payment_method = CharField(max_length=20, null=False, blank=False)
    order = ForeignKey('core.Order', on_delete=CASCADE, blank=True, null=True,
                       help_text=_('If specified, the order will be processed'), related_name='payments_transactions')
    process = JSONField(verbose_name=_('processing details'), default=dict)

    objects = TransactionManager()

    def __str__(self):
        return f"{self.balance.user.email} | {self.amount}"

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        indexes = [
            GinIndex(fields=['process']),
        ]
