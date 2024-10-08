from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VibesAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vibes_auth'
    verbose_name = _("Authentication and Authorization")

    def ready(self):
        import vibes_auth.signals
