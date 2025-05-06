from django.urls import path

from core.views import (
    BuyAsBusinessView,
    GlobalSearchView,
)

urlpatterns = [
    path("search/", GlobalSearchView.as_view(), name="global_search"),
    path("orders/buy_as_business/", BuyAsBusinessView.as_view(), name="request_cursed_url"),
]
