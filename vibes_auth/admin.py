from django.contrib import admin
from django.contrib.auth.admin import (
    GroupAdmin as BaseGroupAdmin,
)
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
)
from django.contrib.auth.models import Group as BaseGroup
from django.contrib.auth.models import Permission
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.token_blacklist.admin import (
    BlacklistedTokenAdmin as BaseBlacklistedTokenAdmin,
)
from rest_framework_simplejwt.token_blacklist.admin import (
    OutstandingTokenAdmin as BaseOutstandingTokenAdmin,
)
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken as BaseBlacklistedToken,
)
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken as BaseOutstandingToken,
)

from core.admin import BasicModelAdmin
from core.models import Order
from payments.models import Balance
from vibes_auth.forms import UserForm
from vibes_auth.models import BlacklistedToken, Group, OutstandingToken, User


class BalanceInline(admin.TabularInline):
    model = Balance
    can_delete = False
    extra = 0
    verbose_name = _("balance")
    verbose_name_plural = _("balance")
    is_navtab = True


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    verbose_name = _("order")
    verbose_name_plural = _("orders")
    is_navtab = True


class UserAdmin(BaseUserAdmin, BasicModelAdmin):
    inlines = (BalanceInline, OrderInline)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("personal info"),
            {"fields": ("first_name", "last_name", "phone_number", "avatar")},
        ),
        (
            _("permissions"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_subscribed",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("important dates"), {"fields": ("last_login", "date_joined")}),
        (_("additional info"), {"fields": ("language", "attributes")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "phone_number", "is_verified", "is_active", "is_staff")
    search_fields = ("email", "phone_number")
    list_filter = (
        "is_verified",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_subscribed",
    )
    ordering = ("email",)
    readonly_fields = ("password",)
    form = UserForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("groups", "payments_balance", "orders").prefetch_related(
            Prefetch(
                "user_permissions",
                queryset=Permission.objects.select_related("content_type"),
            )
        )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("attributes") is None:
            obj.attributes = None
        super().save_model(request, obj, form, change)


class GroupAdmin(BaseGroupAdmin, BasicModelAdmin):
    pass


class BlacklistedTokenAdmin(BaseBlacklistedTokenAdmin, BasicModelAdmin):
    pass


class OutstandingTokenAdmin(BaseOutstandingTokenAdmin, BasicModelAdmin):
    pass


admin.site.register(User, UserAdmin)

admin.site.unregister(BaseGroup)
admin.site.register(Group, GroupAdmin)

admin.site.unregister(BaseBlacklistedToken)
admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)

admin.site.unregister(BaseOutstandingToken)
admin.site.register(OutstandingToken, OutstandingTokenAdmin)
