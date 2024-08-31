from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (
    Feedback, Wishlist, Dealer, Stock, ProductImage, Category, Product,
    OrderProduct, Order, Promotion, PromoCode, AttributeGroup,
    ProductAttribute, LocalizedAttribute, PredefinedAttributes
)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('comment', 'rating', 'order_product')
    search_fields = ('comment', 'order_product__product__name')
    list_filter = ('rating',)
    ordering = ('order_product',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email',)
    inlines = []


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('name', 'markup_percent')
    search_fields = ('name',)
    list_filter = ('markup_percent',)
    ordering = ('name',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'dealer', 'sku', 'quantity', 'price')
    search_fields = ('product__name', 'dealer__name', 'sku')
    list_filter = ('dealer', 'quantity', 'price')
    ordering = ('dealer', 'product', 'price')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('alt', 'product', 'priority')
    search_fields = ('alt', 'product__name')
    list_filter = ('priority',)
    ordering = ('priority',)


class CategoryInline(MPTTModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent', 'markup_percent')
    search_fields = ('name',)
    list_filter = ('markup_percent',)
    ordering = ('name',)


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rating', 'price')
    search_fields = ('name', 'category__name', 'tags')
    list_filter = ('category', 'attributes')
    inlines = [ProductImageInline, StockInline]
    ordering = ('name',)


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'buy_price', 'status')
    search_fields = ('order__uuid', 'product__name', 'status')
    list_filter = ('status',)
    ordering = ('order', 'product')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_price')
    search_fields = ('user__email', 'status')
    list_filter = ('status',)
    inlines = [OrderProductInline]
    ordering = ('status',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent')
    search_fields = ('name', 'products__name')
    ordering = ('name',)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'discount_amount', 'start_time', 'end_time', 'used_on')
    search_fields = ('code',)
    list_filter = ('discount_percent', 'discount_amount', 'start_time', 'end_time')
    ordering = ('code',)


@admin.register(AttributeGroup)
class AttributeGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ru')
    search_fields = ('name', 'name_ru')
    ordering = ('name',)


class LocalizedAttributeInline(admin.TabularInline):
    model = LocalizedAttribute
    extra = 1


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'value_type')
    search_fields = ('name', 'group__name')
    list_filter = ('value_type',)
    inlines = [LocalizedAttributeInline]
    ordering = ('name',)


@admin.register(LocalizedAttribute)
class LocalizedAttributeAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'value_ru')
    search_fields = ('attribute__name', 'value', 'value_ru')
    ordering = ('attribute',)


class AttributeGroupInline(admin.TabularInline):
    model = PredefinedAttributes.groups.through
    extra = 1


@admin.register(PredefinedAttributes)
class PredefinedAttributesAdmin(admin.ModelAdmin):
    list_display = ('category',)
    search_fields = ('category__name',)
    inlines = [AttributeGroupInline]
    ordering = ('category',)
