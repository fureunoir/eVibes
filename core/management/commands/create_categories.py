import json

from django.core.management.base import BaseCommand

from core.models import Category
from evibes.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Started creating initial categories...')

        with open(BASE_DIR / 'core/data/initial_categories.json', 'r') as initial_categories_file:
            initial_categories = json.load(initial_categories_file).get('initial_categories', [])

            for initial_category in initial_categories:
                Category.objects.create(name=initial_category['name'],
                                        description=initial_category['description'])
                pass  # TODO: parse initial categories the right way

        self.stdout.write(self.style.SUCCESS('Initial categories created!'))
