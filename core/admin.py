from constance.admin import Config
from constance.admin import ConstanceAdmin as BaseConstanceAdmin
from django.apps import apps
from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.gis.admin import GISModelAdmin
from django.urls import path
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin
from mptt.admin import DraggableMPTTAdmin

from evibes.settings import CONSTANCE_CONFIG, LANGUAGE_CODE

from .forms import OrderForm, OrderProductForm, VendorForm
from .models import (
    Address,
    Attribute,
    AttributeGroup,
    AttributeValue,
    Brand,
    Category,
    Feedback,
    Order,
    OrderProduct,
    Product,
    ProductImage,
    ProductTag,
    PromoCode,
    Promotion,
    Stock,
    Vendor,
    Wishlist,
)


class BasicModelAdmin(ModelAdmin):
    @admin.action(description=str(_("activate selected %(verbose_name_plural)s")))
    def activate_selected(self, request, queryset) -> str:
        queryset.update(is_active=True)
        return ""

    @admin.action(description=str(_("deactivate selected %(verbose_name_plural)s")))
    def deactivate_selected(self, request, queryset) -> str:
        queryset.update(is_active=False)
        return ""

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions["activate_selected"] = (
            self.activate_selected,
            "activate_selected",
            str(_("activate selected %(verbose_name_plural)s")),
        )
        actions["deactivate_selected"] = (
            self.deactivate_selected,
            "deactivate_selected",
            str(_("deactivate selected %(verbose_name_plural)s")),
        )
        return actions


class AttributeValueInline(TabularInline):
    model = AttributeValue
    extra = 0
    is_navtab = True
    verbose_name = _("attribute value")
    verbose_name_plural = _("attribute values")
    autocomplete_fields = ['attribute']


@admin.register(AttributeGroup)
class AttributeGroupAdmin(BasicModelAdmin, TabbedTranslationAdmin):
    list_display = ("name", "modified")
    search_fields = (
        "uuid",
        "name",
    )


@admin.register(Attribute)
class AttributeAdmin(BasicModelAdmin, TabbedTranslationAdmin):
    list_display = ("name", "group", "value_type", "modified")
    list_filter = ("value_type", "group", "is_active")
    search_fields = ("uuid", "name", "group__name")
    autocomplete_fields = ["categories", "group"]


@admin.register(AttributeValue)
class AttributeValueAdmin(BasicModelAdmin, TabbedTranslationAdmin):
    list_display = ("attribute", "value", "modified")
    list_filter = ("attribute__group", "attribute", "is_active")
    search_fields = ("uuid", "value", "attribute__name")

    autocomplete_fields = ["attribute"]


class CategoryChildrenInline(admin.TabularInline):
    model = Category
    fk_name = "parent"
    extra = 0
    fields = ("name", "description", "is_active", "image", "markup_percent")


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, BasicModelAdmin, TabbedTranslationAdmin):
    mptt_indent_field = "name"
    list_display = ("indented_title", "parent", "is_active", "modified")
    list_filter = ("is_active", "level", "created", "modified")
    list_display_links = ("indented_title",)
    search_fields = (
        "uuid",
        "name",
    )
    inlines = [CategoryChildrenInline]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "name_" + LANGUAGE_CODE.replace("-", "_"),
                    "description",
                    "parent",
                    "is_active",
                    "image",
                    "markup_percent",
                )
            },
        )
    ]
    autocomplete_fields = ["parent"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"name": ("description",)}

    def indented_title(self, instance):
        return instance.name

    indented_title.short_description = _("name")
    indented_title.admin_order_field = "name"


@admin.register(Brand)
class BrandAdmin(BasicModelAdmin, TabbedTranslationAdmin):
    list_display = ("name",)
    list_filter = ("categories", "is_active")
    search_fields = (
        "uuid",
        "name",
        "categories__name",
    )


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0
    is_navtab = True
    verbose_name = _("image")
    verbose_name_plural = _("images")


class StockInline(TabularInline):
    model = Stock
    extra = 0
    is_navtab = True
    verbose_name = _("stock")
    verbose_name_plural = _("stocks")


@admin.register(Product)
class ProductAdmin(BasicModelAdmin, TabbedTranslationAdmin):
    list_display = ("name", "partnumber", "is_active", "category", "brand", "price", "rating", "modified")

    list_filter = (
        "is_active",
        ("tags", admin.RelatedOnlyFieldListFilter),
        ("stocks__vendor", admin.RelatedOnlyFieldListFilter),
        "created",
        "modified",
    )

    search_fields = (
        "name",
        "partnumber",
        "brand__name",
        "category__name",
        "uuid",
    )

    readonly_fields = ("created", "modified", "uuid", "rating", "price")
    autocomplete_fields = ("category", "brand", "tags")

    def price(self, obj):
        return obj.price

    price.short_description = _("price")

    def rating(self, obj):
        return obj.rating

    rating.short_description = _("rating")

    fieldsets = (
        (
            _("basic info"),
            {
                "fields": (
                    "uuid",
                    "partnumber",
                    "is_active",
                    "name",
                    "category",
                    "brand",
                    "description",
                    "tags",
                )
            },
        ),
        (_("important dates"), {"fields": ("created", "modified")}),
    )

    inlines = [AttributeValueInline, ProductImageInline, StockInline]

    def get_changelist(self, request, **kwargs):
        changelist = super().get_changelist(request, **kwargs)
        changelist.filter_input_length = 64
        return changelist


@admin.register(ProductTag)
class ProductTagAdmin(BasicModelAdmin, TabbedTranslationAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Vendor)
class VendorAdmin(BasicModelAdmin):
    list_display = ("name", "markup_percent", "modified")
    list_filter = ("markup_percent", "is_active")
    search_fields = ("name",)
    form = VendorForm


@admin.register(Feedback)
class FeedbackAdmin(BasicModelAdmin):
    list_display = ("order_product", "rating", "comment", "modified")
    list_filter = ("rating", "is_active")
    search_fields = ("order_product__product__name", "comment")


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ("product", "quantity", "buy_price")
    form = OrderProductForm
    is_navtab = True
    verbose_name = _("order product")
    verbose_name_plural = _("order products")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("product").only("product__name")


@admin.register(Order)
class OrderAdmin(BasicModelAdmin):
    list_display = ("human_readable_id", "user", "is_business", "status", "total_price", "buy_time", "modified")
    list_filter = ("status", "buy_time", "modified", "created")
    search_fields = ("user__email", "status", "uuid", "human_readable_id")
    inlines = [OrderProductInline]
    form = OrderForm
    readonly_fields = ("total_price", "total_quantity", "buy_time", "human_readable_id")

    def is_business(self, obj):
        return obj.is_business

    is_business.short_description = _("is business")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            "user",
            "shipping_address",
            "billing_address",
            "order_products",
            "promo_code",
        )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("attributes") is None:
            obj.attributes = None
        if form.cleaned_data.get("notifications") is None:
            obj.attributes = None
        super().save_model(request, obj, form, change)


@admin.register(OrderProduct)
class OrderProductAdmin(BasicModelAdmin):
    list_display = ("order", "product", "quantity", "buy_price", "status", "modified")
    list_filter = ("status",)
    search_fields = ("order__user__email", "product__name")
    form = OrderProductForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("order", "product")

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("attributes") is None:
            obj.attributes = None
        if form.cleaned_data.get("notifications") is None:
            obj.attributes = None
        super().save_model(request, obj, form, change)


@admin.register(PromoCode)
class PromoCodeAdmin(BasicModelAdmin):
    list_display = (
        "code",
        "discount_percent",
        "discount_amount",
        "start_time",
        "end_time",
        "used_on",
    )
    list_filter = ("discount_percent", "discount_amount", "start_time", "end_time")
    search_fields = ("code",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("user")


@admin.register(Promotion)
class PromotionAdmin(BasicModelAdmin, TabbedTranslationAdmin):
    list_display = ("name", "discount_percent", "modified")
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("products")


@admin.register(Stock)
class StockAdmin(BasicModelAdmin):
    list_display = ("product", "vendor", "sku", "quantity", "price", "modified")
    list_filter = ("vendor", "quantity")
    search_fields = ("product__name", "vendor__name", "sku")
    autocomplete_fields = ("product", "vendor")


@admin.register(Wishlist)
class WishlistAdmin(BasicModelAdmin):
    list_display = ("user", "modified")
    search_fields = ("user__email",)


@admin.register(ProductImage)
class ProductImageAdmin(BasicModelAdmin):
    list_display = ("alt", "product", "priority", "modified")
    list_filter = ("priority",)
    search_fields = ("alt", "product__name")
    autocomplete_fields = ("product",)


@admin.register(Address)
class AddressAdmin(GISModelAdmin):
    list_display = ("street", "city", "region", "country", "user")
    list_filter = ("country", "region")
    search_fields = ("raw_data", "street", "city", "postal_code", "user__email")

    gis_widget_kwargs = {
        "attrs": {
            "default_lon": 37.61556,
            "default_lat": 55.75222,
            "default_zoom": 6,
        }
    }


class ConstanceAdmin(BaseConstanceAdmin):
    def get_urls(self):
        info = f"{self.model._meta.app_label}_{self.model._meta.model_name}"
        return [
            path(
                "",
                self.admin_site.admin_view(self.changelist_view),
                name=f"{info}_changelist",
            ),
            path("", self.admin_site.admin_view(self.changelist_view), name=f"{info}_add"),
        ]


class ConstanceConfig:
    class Meta:
        app_label = "core"
        object_name = "Config"
        concrete_model = None
        model_name = module_name = "config"
        verbose_name_plural = _("config")
        abstract = False
        swapped = False
        is_composite_pk = False

        def get_ordered_objects(self):
            return False

        def get_change_permission(self):
            return f"change_{self.model_name}"

        @property
        def app_config(self):
            return apps.get_app_config(self.app_label)

        @property
        def label(self):
            return f"{self.app_label}.{self.object_name}"

        @property
        def label_lower(self):
            return f"{self.app_label}.{self.model_name}"

    _meta = Meta()


admin.site.unregister([Config])  # type: ignore
admin.site.register([ConstanceConfig], ConstanceAdmin)  # type: ignore

admin.site.site_title = f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]}"
admin.site.site_header = "eVibes"
admin.site.index_title = f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]}"
