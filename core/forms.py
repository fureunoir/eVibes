from django import forms

from .models import Order, OrderProduct, Product, Vendor
from .widgets import JSONTableWidget


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "attributes": JSONTableWidget(),
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = "__all__"
        widgets = {
            "authentication": JSONTableWidget(),
        }


class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = "__all__"
        widgets = {
            "notifications": JSONTableWidget(),
            "attributes": JSONTableWidget(),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        widgets = {
            "notifications": JSONTableWidget(),
            "attributes": JSONTableWidget(),
        }
