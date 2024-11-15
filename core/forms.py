from django import forms
from mptt.forms import MPTTAdminForm
from parler.forms import TranslatableModelForm

from .models import Product, Dealer, OrderProduct
from .widgets import JSONTableWidget


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'attributes': JSONTableWidget(),
        }


class DealerForm(forms.ModelForm):
    class Meta:
        model = Dealer
        fields = '__all__'
        widgets = {
            'authentication': JSONTableWidget(),
        }


class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = '__all__'
        widgets = {
            'notifications': JSONTableWidget(),
            'attributes': JSONTableWidget(),
        }

class CategoryForm(MPTTAdminForm, TranslatableModelForm):
    pass
