from constance import config
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import CallbackAPIView

payment_router = DefaultRouter()

urlpatterns = [
    # path(r'', include(payment_router.urls)),
    path(f'<str:uuid>/callback/', CallbackAPIView.as_view())
]
