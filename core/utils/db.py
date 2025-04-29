from django.db.models import Model
from django.utils.translation import gettext_lazy as _


def list_to_queryset(model: Model, data: list):
    if not isinstance(model, Model):
        raise ValueError(_(f"{model} must be model"))
    if not isinstance(data, list):
        raise ValueError(_(f"{data} must be list object"))

    pk_list = [obj.pk for obj in data]
    return model.objects.filter(pk__in=pk_list)
