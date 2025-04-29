from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payments.views import CallbackAPIView, DepositView
from payments.viewsets import TransactionViewSet

payment_router = DefaultRouter()
payment_router.register(prefix=r"transactions", viewset=TransactionViewSet, basename="transactions")

urlpatterns = [
    path(r"", include(payment_router.urls)),
    path(r"deposit/", DepositView.as_view()),
    path(r"<str:uuid>/callback/<str:gateway>/", CallbackAPIView.as_view()),
]
