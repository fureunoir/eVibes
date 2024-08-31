from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from vibes_auth.models import User
from payments.models import Balance
from core.models import Wishlist, Order


class BalanceInline(admin.TabularInline):
    model = Balance
    can_delete = False
    readonly_fields = ('amount',)
    extra = 0
    verbose_name = _("Balance")
    verbose_name_plural = _("Balance")


class WishlistInline(admin.TabularInline):
    model = Wishlist
    can_delete = False
    extra = 0
    verbose_name = _("Wishlist")
    verbose_name_plural = _("Wishlist")


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    verbose_name = _("Order")
    verbose_name_plural = _("Orders")


class UserAdmin(BaseUserAdmin):
    inlines = (BalanceInline, WishlistInline, OrderInline)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('phone_number', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_verified', 'is_subscribed', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Additional info'), {'fields': ('recently_viewed',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'phone_number', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('email', 'phone_number')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'is_subscribed')
    ordering = ('email',)


admin.site.register(User, UserAdmin)
