from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView

# from core.schema import schema
from core.views import favicon_view, index, CustomSwaggerView, CustomRedocView
from evibes.settings import SPECTACULAR_PLATFORM_SETTINGS

urlpatterns = [
               # path(r'graphql/', csrf_exempt(CustomGraphQLView.as_view(graphiql=True, schema=schema))),
               path(r'docs/', SpectacularAPIView.as_view(urlconf='evibes.api_urls', custom_settings=SPECTACULAR_PLATFORM_SETTINGS),
                    name='schema-platform'),
               path(r'docs/swagger/', CustomSwaggerView.as_view(url_name='schema-platform'),
                    name='swagger-ui-platform'),
               path(r'docs/redoc/', CustomRedocView.as_view(url_name='schema-platform'),
                    name='redoc-ui-platform'),
               path(r'i18n/', include("django.conf.urls.i18n")),
               path(r'favicon.ico/', favicon_view),
               path(r'', index),
               path(r'', include('core.urls')),
               path(r'auth/', include('vibes_auth.urls')),
               path(r'geo/', include('geo.urls')),
               path('payments', include('payments.urls')),
               ] + i18n_patterns(path("admin/", admin.site.urls))

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
