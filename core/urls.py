from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import index, SupportedLanguagesView
from core.viewsets import ProductViewSet, OrderViewSet, WishlistViewSet, AttributeGroupViewSet, BrandViewSet, \
    CategoryViewSet, DealerViewSet, FeedbackViewSet, StockViewSet, PromoCodeViewSet, PromotionViewSet

core_router = DefaultRouter()
core_router.register(r'products', ProductViewSet, basename='products')
core_router.register(r'orders', OrderViewSet, basename='orders')
core_router.register(r'wishlists', WishlistViewSet, basename='wishlists')
core_router.register(r'attribute_groups', AttributeGroupViewSet, basename='attribute_groups')
core_router.register(r'brands', BrandViewSet, basename='brands')
core_router.register(r'categories', CategoryViewSet, basename='categories')
core_router.register(r'dealers', DealerViewSet, basename='dealers')
core_router.register(r'feedbacks', FeedbackViewSet, basename='feedbacks')
core_router.register(r'stocks', StockViewSet, basename='stocks')
core_router.register(r'promo_codes', PromoCodeViewSet, basename='promo_codes')
core_router.register(r'promotions', PromotionViewSet, basename='promotions')

urlpatterns = [
    path(r'core/', include(core_router.urls)),
    path(r'config/languages', SupportedLanguagesView.as_view(), name='supported_languages'),
]
