from django.core.management.base import BaseCommand

from core.utils.caching import set_default_cache


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Started setting default cache values..."))

        set_default_cache()

        self.stdout.write(self.style.SUCCESS("Setting default cache values completed!"))
