from django.contrib.sitemaps import Sitemap
from django.utils.text import slugify

from core.models import Brand, Category, Product
from evibes.settings import LANGUAGE_CODE


class ProductSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.9
    limit = 40000

    def items(self):
        return (
            Product.objects.filter(
                is_active=True,
                brand__is_active=True,
                category__is_active=True,
            )
            .only("uuid", "name", "modified", "slug")
            .order_by("-modified")
        )

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        return f"/{LANGUAGE_CODE}/product/{obj.slug}"


class CategorySitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7
    limit = 40000

    def items(self):
        return Category.objects.filter(is_active=True).only("uuid", "name", "modified").order_by("-modified")

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        slug = slugify(obj.name)
        return f"/{LANGUAGE_CODE}/catalog/{obj.uuid}/{slug}"


class BrandSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6
    limit = 40000

    def items(self):
        return Brand.objects.filter(is_active=True).only("uuid", "name", "modified").order_by("-modified")

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        slug = slugify(obj.name)
        return f"/{LANGUAGE_CODE}/brand/{obj.uuid}/{slug}"
