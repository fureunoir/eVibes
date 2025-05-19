from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Index
from django.utils.translation import gettext_lazy as _

from core.abstract import NiceModel
from geo.managers import AddressManager


class Address(NiceModel):
    street = models.CharField(_("street"), max_length=255, null=True)  # noqa: DJ001
    district = models.CharField(_("district"), max_length=255, null=True)  # noqa: DJ001
    city = models.CharField(_("city"), max_length=100, null=True)  # noqa: DJ001
    region = models.CharField(_("region"), max_length=100, null=True)  # noqa: DJ001
    postal_code = models.CharField(_("postal code"), max_length=20, null=True)  # noqa: DJ001
    country = models.CharField(_("country"), max_length=40, null=True)  # noqa: DJ001

    location = gis_models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
        help_text=_("geolocation point: (longitude, latitude)")
    )

    raw_data = models.JSONField(
        blank=True,
        null=True,
        help_text=_("full JSON response from geocoder for this address")
    )

    api_response = models.JSONField(
        blank=True,
        null=True,
        help_text=_("stored JSON response from the geocoding service")
    )

    user = models.ForeignKey(
        to="vibes_auth.User",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    objects = AddressManager()

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        indexes = [
            Index(fields=["location"]),
        ]

    def __str__(self):
        base = f"{self.street}, {self.city}, {self.country}"
        return f"{base} for {self.user.email}" if self.user else base
