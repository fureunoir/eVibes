from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView

from core.schema import schema
from core.views import favicon_view, CustomGraphQLView, CustomSwaggerView, CustomRedocView
from evibes.settings import SPECTACULAR_B2B_SETTINGS

urlpatterns = [
    path(r'graphql/', csrf_exempt(CustomGraphQLView.as_view(graphiql=True, schema=schema))),
    path(r'docs/', SpectacularAPIView.as_view(urlconf='evibes.api_urls', custom_settings=SPECTACULAR_B2B_SETTINGS),
         name='schema-b2b'),
    path(r'docs/swagger/', CustomSwaggerView.as_view(url_name='schema-b2b'),
         name='swagger-ui-b2b'),
    path(r'docs/redoc/', CustomRedocView.as_view(url_name='schema-b2b'),
         name='redoc-ui-b2b'),
    path(r'favicon.ico/', favicon_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
