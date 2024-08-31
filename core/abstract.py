import uuid

from django.db.models import UUIDField, BooleanField, Model
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class NiceModel(Model):
    uuid = UUIDField(verbose_name=_('UUID'), primary_key=True, default=uuid.uuid4, editable=False)
    active = BooleanField(default=True, verbose_name=_('active'))
    created = CreationDateTimeField(_('created'), editable=True)
    modified = ModificationDateTimeField(_('modified'))

    def save(self, **kwargs):
        self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
        super().save(**kwargs)

    class Meta:
        abstract = True
        get_latest_by = 'modified'
