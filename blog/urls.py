from django.urls import include, path
from rest_framework.routers import DefaultRouter

from blog.viewsets import PostViewSet

payment_router = DefaultRouter()
payment_router.register(prefix=r"posts", viewset=PostViewSet, basename="posts")

urlpatterns = [
    path(r"", include(payment_router.urls)),
]
