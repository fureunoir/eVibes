from django.urls import path, include
from rest_framework.routers import DefaultRouter

from vibes_auth.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from vibes_auth.viewsets import UserViewSet

auth_router = DefaultRouter()
auth_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path(r'auth/obtain/', TokenObtainPairView.as_view(), name='token_create'),
    path(r'auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(r'auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path(r'', include(auth_router.urls)),
]