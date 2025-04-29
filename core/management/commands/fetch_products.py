from django.core.management.base import BaseCommand

from core.tasks import update_products_task


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting fetching products task in worker container..."))

        update_products_task.delay()

        self.stdout.write(self.style.SUCCESS("Started fetching products task in worker container without errors!"))
