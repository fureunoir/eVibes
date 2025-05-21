import importlib
import os

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

DEEPL_API_URL = "https://api.deepl.com/v2/translate"

DEEPL_TARGET_LANGUAGES_MAPPING = {
    "en-gb": "EN-GB",
    "ar-ar": "AR",
    "cs-cz": "CS",
    "da-dk": "DA",
    "de-de": "DE",
    "en-us": "EN-US",
    "es-es": "ES",
    "fr-fr": "FR",
    "hi-in": "unsupported",
    "it-it": "IT",
    "ja-jp": "JA",
    "kk-kz": "unsupported",
    "nl-nl": "NL",
    "pl-pl": "PL",
    "pt-br": "PT-BR",
    "ro-ro": "RO",
    "ru-ru": "RU",
    "zh-hans": "ZH-HANS",
}


class Command(BaseCommand):
    help = (
        "Translate a model field into another language via DeepL and store it "
        "in the translated_<lang> field created by django-modeltranslation."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-t", "--target", required=True,
            help=(
                "Dotted path to the field to translate, "
                "e.g. core.models.Product.description"
            ),
        )
        parser.add_argument(
            "-l", "--language", required=True,
            help=(
                "Modeltranslation language code to translate into, "
                "e.g. de-de, fr-fr, zh-hans"
            ),
        )

    def handle(self, *args, **options):
        target = options["target"]
        lang = options["language"].lower()

        if lang not in DEEPL_TARGET_LANGUAGES_MAPPING:
            raise CommandError(f"Unknown language '{lang}'.")
        deepl_lang = DEEPL_TARGET_LANGUAGES_MAPPING[lang]
        if deepl_lang == "unsupported":
            raise CommandError(f"DeepL does not support translating into '{lang}'.")

        try:
            module_path, model_name, field_name = target.rsplit(".", 2)
        except ValueError:
            raise CommandError(
                "Invalid target format. Use app.module.Model.field, e.g. core.models.Product.description"
            )

        try:
            module = importlib.import_module(module_path)
            model = getattr(module, model_name)
        except (ImportError, AttributeError) as e:
            raise CommandError(f"Could not import model '{model_name}' from '{module_path}': {e}")

        dest_suffix = lang.replace("-", "_")
        dest_field = f"{field_name}_{dest_suffix}"

        if not hasattr(model, dest_field):
            raise CommandError(
                f"Model '{model_name}' has no field '{dest_field}'. "
                "Did you run makemigrations/migrate after setting up modeltranslation?"
            )

        auth_key = os.environ.get("DEEPL_AUTH_KEY")
        if not auth_key:
            raise CommandError("Environment variable DEEPL_AUTH_KEY is not set.")

        qs = model.objects.exclude(**{f"{field_name}__isnull": True}) \
            .exclude(**{f"{field_name}": ""})
        total = qs.count()
        if total == 0:
            self.stdout.write("No instances with non-empty source field found.")
            return

        self.stdout.write(f"Translating {total} objects from '{field_name}' into '{dest_field}'.")

        for obj in qs.iterator():
            src_text = getattr(obj, field_name)
            existing = getattr(obj, dest_field, None)
            if existing:
                self.stdout.write(f"Skipping {obj.pk}: '{dest_field}' already set.")
                continue

            resp = requests.post(
                DEEPL_API_URL,
                data={
                    "auth_key": auth_key,
                    "text": src_text,
                    "target_lang": deepl_lang,
                },
                timeout=30,
            )
            if resp.status_code != 200:
                self.stderr.write(
                    f"DeepL API error for {obj.pk}: {resp.status_code} {resp.text}"
                )
                continue

            data = resp.json()
            try:
                translated = data["translations"][0]["text"]
            except (KeyError, IndexError):
                self.stderr.write(f"Unexpected DeepL response for {obj.pk}: {data}")
                continue

            setattr(obj, dest_field, translated)
            try:
                with transaction.atomic():
                    obj.save(update_fields=[dest_field])
            except Exception as e:
                self.stderr.write(f"Error saving {obj.pk}: {e}")
            else:
                self.stdout.write(f"✓ {obj.pk}")

        self.stdout.write(self.style.SUCCESS("Done."))
