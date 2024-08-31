from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from core.schema import schema
from core.views import favicon_view, CustomGraphQLView

urlpatterns = [
                  path('graphql/', csrf_exempt(CustomGraphQLView.as_view(graphiql=True, schema=schema))),
                  path('docs/', SpectacularAPIView.as_view(), name='schema'),
                  path('docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
                  path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
                  path("i18n/", include("django.conf.urls.i18n")),
                  path('favicon.ico', favicon_view),
                  path('', include('vibes_auth.urls')),
              ] + i18n_patterns(path("admin/", admin.site.urls))

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
