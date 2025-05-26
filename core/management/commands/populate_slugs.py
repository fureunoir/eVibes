import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Product

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate slug field for all Product instances"

    def handle(self, *args, **options):
        qs = Product.objects.filter(slug__isnull=True)
        total = qs.count()
        self.stdout.write(f"Starting slug population for {total} products")

        for idx, product in enumerate(qs.iterator(), start=1):
            try:
                product.slug = None
                with transaction.atomic():
                    product.save(update_fields=["slug"])

                self.stdout.write(
                    self.style.SUCCESS(f"[{idx}/{total}] (Product ID: {product.pk}) slug set to '{product.slug}'")
                )
            except Exception as e:
                logger.exception(f"Product {product.pk}: slug population failed")
                self.stderr.write(self.style.ERROR(f"[{idx}/{total}] (Product ID: {product.pk}) ERROR: {e}"))

        self.stdout.write(self.style.SUCCESS("Slug population complete."))
