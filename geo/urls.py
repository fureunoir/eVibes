from django.urls import include, path
from rest_framework.routers import DefaultRouter

from geo.viewsets import AddressViewSet

geo_router = DefaultRouter()
geo_router.register(r"addresses", AddressViewSet, basename="addresses")

urlpatterns = [
    path(r"", include(geo_router.urls)),
]
