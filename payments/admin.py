from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.admin import BasicModelAdmin
from payments.forms import TransactionForm
from payments.models import Balance, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    form = TransactionForm
    extra = 1
    is_navtab = True
    verbose_name = _("transaction")
    verbose_name_plural = _("transactions")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("order")


class BalanceAdmin(BasicModelAdmin):
    inlines = (TransactionInline,)
    list_display = ("user", "amount")
    search_fields = ("user__email",)
    ordering = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("transactions", "user")


class TransactionAdmin(BasicModelAdmin):
    list_display = ("balance", "amount", "currency", "payment_method", "order")
    search_fields = ("balance__user__email", "currency", "payment_method")
    list_filter = ("currency", "payment_method")
    ordering = ("balance",)
    form = TransactionForm


admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
