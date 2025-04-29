from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from core.models import Attribute, AttributeGroup, AttributeValue, Brand, Category, Product, ProductTag, Promotion


@register(AttributeGroup)
class AttributeGroupOptions(TranslationOptions):
    fields = ("name",)


@register(Attribute)
class AttributeOptions(TranslationOptions):
    fields = ("name",)


@register(AttributeValue)
class AttributeValueOptions(TranslationOptions):
    fields = ("value",)


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ("description", )


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(ProductTag)
class ProductTagOptions(TranslationOptions):
    fields = ("name",)


@register(Promotion)
class PromotionOptions(TranslationOptions):
    fields = ("name", "description")
