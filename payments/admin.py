from django.contrib import admin

from payments.models import Balance, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 1


class BalanceAdmin(admin.ModelAdmin):
    inlines = (TransactionInline,)
    list_display = ('user', 'amount')
    search_fields = ('user__email',)
    ordering = ('user',)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('balance', 'amount', 'currency', 'payment_method', 'order')
    search_fields = ('balance__user__email', 'currency', 'payment_method')
    list_filter = ('currency', 'payment_method')
    ordering = ('balance',)


admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
