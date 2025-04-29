import os
import re
import tempfile

import polib
import requests
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

DEEPL_TARGET_LANGUAGES_MAPPING = {
    "en-GB": "EN-GB",
    "ar-AR": "AR",
    "cs-CZ": "CS",
    "da-DK": "DA",
    "de-DE": "DE",
    "en-US": "EN-US",
    "es-ES": "ES",
    "fr-FR": "FR",
    "hi-IN": "unsupported",
    "it-IT": "IT",
    "ja-JP": "JA",
    "kk-KZ": "unsupported",
    "nl-NL": "NL",
    "pl-PL": "PL",
    "pt-BR": "PT-BR",
    "ro-RO": "RO",
    "ru-RU": "RU",
    "zh-hans": "ZH-HANS",
}


def load_po_sanitized(path):
    """
    Attempt to load .po via polib; on OSError, normalize any '#,fuzzy' flags
    (inserting the missing space) and strip blank-header entries, then parse again.
    """
    try:
        return polib.pofile(path)
    except OSError:
        text = open(path, encoding="utf-8").read()
        # ensure any "#,fuzzy" becomes "#, fuzzy" so polib can parse flags
        text = re.sub(r'^#,(?!\s)', '#, ', text, flags=re.MULTILINE)

        # split off the header entry by the first blank line
        parts = text.split("\n\n", 1)
        header = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        # drop any stray blank msgid/msgstr pairs that can also break parsing
        rest_clean = re.sub(
            r'^msgid ""\s*\nmsgstr ""\s*\n?', "",
            rest,
            flags=re.MULTILINE
        )

        sanitized = header + "\n\n" + rest_clean

        # write to a temp file and parse
        tmp = tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".po", encoding="utf-8"
        )
        tmp.write(sanitized)
        tmp.flush()
        tmp.close()
        try:
            po = polib.pofile(tmp.name)
        finally:
            os.unlink(tmp.name)
        return po


class Command(BaseCommand):
    help = "Merge msgid/msgstr from en_GB PO into target-language POs via DeepL"

    def add_arguments(self, parser):
        parser.add_argument(
            "-l", "--language",
            dest="target_languages",
            action="append",
            required=True,
            metavar="LANG",
            help="Locale code for translation, e.g. de-DE, fr-FR. Can be used multiple times."
        )
        parser.add_argument(
            "-a", "--app",
            dest="target_apps",
            action="append",
            required=True,
            metavar="APP",
            help="Application name for translation, e.g. core, geo. Can be used multiple times."
        )

    def handle(self, *args, **options):
        target_langs = options["target_languages"]
        target_apps = set(options["target_apps"])
        auth_key = os.environ.get("DEEPL_AUTH_KEY")
        if not auth_key:
            raise CommandError("Environment variable DEEPL_AUTH_KEY is not set.")

        for target_lang in target_langs:
            api_code = DEEPL_TARGET_LANGUAGES_MAPPING.get(target_lang)
            if not api_code:
                self.stdout.write(self.style.WARNING(f"Ignoring unknown language '{target_lang}'"))
                continue
            if api_code == "unsupported":
                self.stdout.write(self.style.WARNING(f"Skipping unsupported language '{target_lang}'"))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(
                f"→ Translating into {target_lang} (DeepL code: {api_code})"
            ))

            for app_config in apps.get_app_configs():
                if app_config.label not in target_apps:
                    continue

                # 1) load & sanitize English source .po
                en_po_path = os.path.join(
                    app_config.path, "locale", "en_GB", "LC_MESSAGES", "django.po"
                )
                if not os.path.isfile(en_po_path):
                    self.stdout.write(self.style.WARNING(
                        f"  • {app_config.label}: no en_GB PO found, skipping"
                    ))
                    continue

                self.stdout.write(f"  • {app_config.label}: loading English PO…")
                en_po = load_po_sanitized(en_po_path)

                # collect all non-obsolete entries with a msgid
                en_entries = [
                    e for e in en_po
                    if e.msgid and not e.obsolete
                ]
                # map msgid -> source text (prefer existing msgstr if any)
                source_texts = {
                    e.msgid: (e.msgstr or e.msgid)
                    for e in en_entries
                }

                # 2) load (or create) the target .po
                tgt_po_dir = os.path.join(
                    app_config.path,
                    "locale",
                    target_lang.replace("-", "_"),
                    "LC_MESSAGES"
                )
                os.makedirs(tgt_po_dir, exist_ok=True)
                tgt_po_path = os.path.join(tgt_po_dir, "django.po")

                if os.path.exists(tgt_po_path):
                    self.stdout.write(f"      loading existing {target_lang} PO…")
                    try:
                        old_tgt = load_po_sanitized(tgt_po_path)
                    except Exception:
                        self.stdout.write(self.style.WARNING(
                            "      ! existing target PO parse error, starting fresh"
                        ))
                        old_tgt = None
                else:
                    old_tgt = None

                # rebuild a new PO file in the same order as English
                new_po = polib.POFile()
                new_po.metadata = en_po.metadata.copy()
                new_po.metadata["Language"] = target_lang

                for e in en_entries:
                    prev = old_tgt.find(e.msgid) if old_tgt else None
                    entry = polib.POEntry(
                        msgid=e.msgid,
                        msgstr=(prev.msgstr if prev and prev.msgstr else ""),
                        msgctxt=e.msgctxt,
                        comment=e.comment,
                        tcomment=e.tcomment,
                        occurrences=e.occurrences,
                        flags=e.flags,
                    )
                    new_po.append(entry)

                # 3) find which still need translating
                to_translate = [e for e in new_po if not e.msgstr]
                if not to_translate:
                    self.stdout.write(self.style.WARNING(
                        f"      ! all entries already translated for {app_config.label}"
                    ))
                    continue

                texts = [source_texts[e.msgid] for e in to_translate]

                # 4) call DeepL
                resp = requests.post(
                    "https://api-free.deepl.com/v2/translate",
                    data={
                        "auth_key":    auth_key,
                        "target_lang": api_code,
                        "text":        texts,
                    }
                )
                try:
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as exc:
                    raise CommandError(
                        f"DeepL API error for {app_config.label}|{target_lang}: "
                        f"{exc} – {resp.text}"
                    )

                translations = data.get("translations", [])
                if len(translations) != len(to_translate):
                    raise CommandError(
                        f"Unexpected translations count: {len(translations)} vs {len(to_translate)}"
                    )

                for entry, trans in zip(to_translate, translations):
                    entry.msgstr = trans["text"]

                # 5) save merged & translated PO
                new_po.save(tgt_po_path)
                self.stdout.write(self.style.SUCCESS(
                    f"      ✔ saved {target_lang} PO: {tgt_po_path}"
                ))

        self.stdout.write(self.style.SUCCESS("All translations complete."))
