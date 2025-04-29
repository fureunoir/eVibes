from django.forms import ModelForm

from core.widgets import JSONTableWidget
from vibes_auth.models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            "attributes": JSONTableWidget(),
        }
