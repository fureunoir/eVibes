from django import forms

from core.widgets import JSONTableWidget
from payments.models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = "__all__"
        widgets = {
            "process": JSONTableWidget(),
        }
