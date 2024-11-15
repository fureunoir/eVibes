# core/admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from parler.admin import TranslatableAdmin

from evibes.settings import CONSTANCE_CONFIG
from .models import (
    AttributeGroup, Attribute, AttributeValue,
    Category, CategoryAttribute, Brand, Product,
    ProductAttributeValue, Dealer, Feedback,
    Order, OrderProduct, ProductTag,
    ProductImage, PromoCode, Promotion,
    Stock, Wishlist
)
from .forms import DealerForm, OrderProductForm, CategoryForm


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1


@admin.register(AttributeGroup)
class AttributeGroupAdmin(TranslatableAdmin):
    list_display = ('name',)
    search_fields = ('translations__name',)


@admin.register(Attribute)
class AttributeAdmin(TranslatableAdmin):
    list_display = ('name', 'group', 'value_type')
    list_filter = ('value_type', 'group')
    search_fields = ('translations__name', 'group__translations__name')
    inlines = [AttributeValueInline]


@admin.register(AttributeValue)
class AttributeValueAdmin(TranslatableAdmin):
    list_display = ('attribute', 'value')
    list_filter = ('attribute__group', 'attribute')
    search_fields = ('translations__value', 'attribute__translations__name')


class CategoryAttributeInline(admin.TabularInline):
    model = CategoryAttribute
    extra = 1


class TranslatableMPTTAdmin(TranslatableAdmin, MPTTModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(TranslatableMPTTAdmin, DraggableMPTTAdmin):
    form = CategoryForm
    list_display = ('tree_actions', 'indented_title', 'parent', 'is_active')
    list_display_links = ('indented_title',)
    search_fields = ('translations__name',)
    inlines = [CategoryAttributeInline]

    def get_prepopulated_fields(self, request, obj=None):
        return {'name': ('description',)}

    def indented_title(self, instance):
        return instance.name

    indented_title.short_description = _('Name')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__translations__name')


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'rating')
    list_filter = ('category', 'brand', 'created', 'modified')
    search_fields = ('translations__name', 'category__translations__name', 'brand__name')
    inlines = [ProductAttributeValueInline, ProductImageInline, StockInline]
    readonly_fields = ('created', 'modified')
    fieldsets = (
        (_('Basic Info'), {'fields': ('name', 'category', 'brand', 'description', 'tags')}),
        #(_('Attributes'), {'fields': ('attributes',)}),
        (_('Important dates'), {'fields': ('created', 'modified')}),
    )


@admin.register(ProductTag)
class ProductTagAdmin(TranslatableAdmin):
    list_display = ('name',)
    search_fields = ('translations__name',)


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('name', 'markup_percent')
    list_filter = ('markup_percent',)
    search_fields = ('name',)
    form = DealerForm


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('order_product', 'rating', 'comment')
    list_filter = ('rating',)
    search_fields = ('order_product__product__translations__name', 'comment')


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'buy_time')
    list_filter = ('status', 'buy_time')
    search_fields = ('user__email', 'status')
    inlines = [OrderProductInline]
    readonly_fields = ('total_price', 'total_quantity')


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'buy_price', 'status')
    list_filter = ('status',)
    search_fields = ('order__user__email', 'product__translations__name')
    form = OrderProductForm


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'discount_amount', 'start_time', 'end_time', 'used_on')
    list_filter = ('discount_percent', 'discount_amount', 'start_time', 'end_time')
    search_fields = ('code',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent')
    search_fields = ('name',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'dealer', 'sku', 'quantity', 'price')
    list_filter = ('dealer', 'quantity')
    search_fields = ('product__translations__name', 'dealer__name', 'sku')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('alt', 'product', 'priority')
    list_filter = ('priority',)
    search_fields = ('alt', 'product__translations__name')


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute_value')
    list_filter = ('attribute_value__attribute__group', 'attribute_value__attribute')
    search_fields = ('product__translations__name', 'attribute_value__translations__value')


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ('category', 'attribute')
    list_filter = ('category', 'attribute__group')
    search_fields = ('category__translations__name', 'attribute__translations__name')


admin.site.site_title = f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]} Admin"
admin.site.site_header = f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]}"
admin.site.index_title = f"{CONSTANCE_CONFIG.get('PROJECT_NAME')[0]}"
