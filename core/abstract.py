import uuid

import graphene
from django.db.models import UUIDField, BooleanField, Model
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class NiceModel(Model):
    id = None
    uuid = UUIDField(verbose_name=_('UUID'), primary_key=True, default=uuid.uuid4, editable=False)
    is_active = BooleanField(default=True, verbose_name=_('is active'))
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    def save(self, **kwargs):
        self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
        super().save(**kwargs)

    class Meta:
        abstract = True
        get_latest_by = 'modified'


class BaseMutation(graphene.Mutation):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def mutate(**kwargs):
        pass
