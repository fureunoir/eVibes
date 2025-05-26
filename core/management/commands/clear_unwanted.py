from collections import defaultdict

from django.core.management.base import BaseCommand

from core.models import Category, Product, Stock


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting clearing unwanted data..."))

        # 1. Clean up duplicate Stock entries per product and vendor:
        # Group stocks by (product, vendor)
        stocks_by_group = defaultdict(list)
        for stock in Stock.objects.all().order_by("modified"):
            key = (stock.product_id, stock.vendor)
            stocks_by_group[key].append(stock)

        stock_deletions = []
        for group in stocks_by_group.values():
            if len(group) <= 1:
                continue

            # Split the group into admin-edited and never-edited
            admin_edited = [s for s in group if s.modified > s.created]
            if admin_edited:
                # Keep the admin-edited stock with the latest modified
                record_to_keep = max(admin_edited, key=lambda s: s.modified)
            else:
                # None were admin-edited; keep the one with the latest modified field
                record_to_keep = max(group, key=lambda s: s.modified)

            # Mark all stocks (except the designated one) for deletion.
            for s in group:
                if s.id != record_to_keep.id:
                    stock_deletions.append(s.id)

        if stock_deletions:
            Stock.objects.filter(id__in=stock_deletions).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {len(stock_deletions)} duplicate stock entries."))

        # 2. Clean up duplicate Category entries based on name (case-insensitive)
        category_groups = defaultdict(list)
        for cat in Category.objects.all().order_by("modified"):
            key = cat.name.lower()
            category_groups[key].append(cat)

        categories_to_delete = []
        total_product_updates = 0
        for cat_list in category_groups.values():
            if len(cat_list) <= 1:
                continue

            # Check for admin-edited categories in this group.
            admin_edited = [c for c in cat_list if c.modified > c.created]
            if admin_edited:
                keep_category = max(admin_edited, key=lambda c: c.modified)
            else:
                keep_category = max(cat_list, key=lambda c: c.modified)

            for duplicate in cat_list:
                if duplicate.id == keep_category.id:
                    continue
                total_product_updates += Product.objects.filter(category=duplicate).update(category=keep_category)
                categories_to_delete.append(duplicate.id)

        if categories_to_delete:
            Category.objects.filter(id__in=categories_to_delete).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Replaced category for {total_product_updates} product(s) "
                    f"and deleted {len(categories_to_delete)} duplicate categories."
                )
            )

        # 3. For Products without stocks: set is_active = False.
        inactive_products = Product.objects.filter(stock__isnull=True)
        count_inactive = inactive_products.count()
        if count_inactive:
            inactive_products.update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f"Set {count_inactive} product(s) as inactive due to missing stocks."))

        # 4. Delete stocks without an associated product.
        orphan_stocks = Stock.objects.filter(product__isnull=True)
        orphan_count = orphan_stocks.count()
        if orphan_count:
            orphan_stocks.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {orphan_count} stock(s) without an associated product."))

        self.stdout.write(self.style.SUCCESS("Started fetching products task in worker container without errors!"))
