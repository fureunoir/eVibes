import uuid

from django.db.models import BooleanField, Model, UUIDField
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class NiceModel(Model):
    id = None
    uuid = UUIDField(
        verbose_name=_("unique id"),
        help_text=_("unique id is used to surely identify any database object"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    is_active = BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("if set to false, this object can't be seen by users without needed permission"),
    )
    created = CreationDateTimeField(_("created"), help_text=_("when the object first appeared on the database"))
    modified = ModificationDateTimeField(_("modified"), help_text=_("when the object was last modified"))

    def save(self, **kwargs):
        self.update_modified = kwargs.pop("update_modified", getattr(self, "update_modified", True))
        super().save(**kwargs)

    class Meta:
        abstract = True
        get_latest_by = "modified"
