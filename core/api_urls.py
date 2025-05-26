from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.sitemaps import BrandSitemap, CategorySitemap, ProductSitemap
from core.views import (
    CacheOperatorView,
    ContactUsView,
    GlobalSearchView,
    RequestCursedURLView,
    SupportedLanguagesView,
    WebsiteParametersView,
    download_digital_asset_view,
    sitemap_detail,
    sitemap_index,
)
from core.viewsets import (
    AddressViewSet,
    AttributeGroupViewSet,
    BrandViewSet,
    CategoryViewSet,
    FeedbackViewSet,
    OrderViewSet,
    ProductViewSet,
    PromoCodeViewSet,
    PromotionViewSet,
    StockViewSet,
    VendorViewSet,
    WishlistViewSet,
)

core_router = DefaultRouter()
core_router.register(r"products", ProductViewSet, basename="products")
core_router.register(r"orders", OrderViewSet, basename="orders")
core_router.register(r"wishlists", WishlistViewSet, basename="wishlists")
core_router.register(r"attribute_groups", AttributeGroupViewSet, basename="attribute_groups")
core_router.register(r"brands", BrandViewSet, basename="brands")
core_router.register(r"categories", CategoryViewSet, basename="categories")
core_router.register(r"vendors", VendorViewSet, basename="vendors")
core_router.register(r"feedbacks", FeedbackViewSet, basename="feedbacks")
core_router.register(r"stocks", StockViewSet, basename="stocks")
core_router.register(r"promo_codes", PromoCodeViewSet, basename="promo_codes")
core_router.register(r"promotions", PromotionViewSet, basename="promotions")
core_router.register(r"addresses", AddressViewSet, basename="addresses")

sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "brands": BrandSitemap,
}

urlpatterns = [
    path("core/", include(core_router.urls)),
    path(
        "sitemap.xml", sitemap_index, {"sitemaps": sitemaps, "sitemap_url_name": "sitemap-detail"}, name="sitemap-index"
    ),
    path("sitemap-<section>.xml", sitemap_detail, {"sitemaps": sitemaps}, name="sitemap-detail"),
    path("sitemap-<section>-<int:page>.xml", sitemap_detail, {"sitemaps": sitemaps}, name="sitemap-detail"),
    path("download/<str:order_product_uuid>/", download_digital_asset_view, name="download_digital_asset"),
    path("search/", GlobalSearchView.as_view(), name="global_search"),
    path("app/cache/", CacheOperatorView.as_view(), name="cache_operator"),
    path("app/languages/", SupportedLanguagesView.as_view(), name="supported_languages"),
    path("app/parameters/", WebsiteParametersView.as_view(), name="parameters"),
    path("app/contact_us/", ContactUsView.as_view(), name="contact_us"),
    path("app/request_cursed_url/", RequestCursedURLView.as_view(), name="request_cursed_url"),
]
