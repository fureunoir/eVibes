import os
import re
from tempfile import NamedTemporaryFile

import polib
import requests
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

# Mapping from Django locale codes to DeepL API codes
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

# Patterns to identify placeholders
PLACEHOLDER_REGEXES = [
    re.compile(r"\{[^}]+"),  # {name}, {product_uuid}
    re.compile(r"%\([^)]+\)[sd]"),  # %(name)s, %(count)d
]


def placeholderize(text: str) -> tuple[str, list[str]]:
    """
    Replace placeholders with tokens and collect originals.
    Returns (protected_text, placeholders_list).
    """
    placeholders: list[str] = []

    def _repl(match: re.Match) -> str:
        idx = len(placeholders)
        placeholders.append(match.group(0))
        return f"__PH_{idx}__"

    for rx in PLACEHOLDER_REGEXES:
        text = rx.sub(_repl, text)
    return text, placeholders


def deplaceholderize(text: str, placeholders: list[str]) -> str:
    """
    Restore tokens back to original placeholders.
    """
    for idx, ph in enumerate(placeholders):
        text = text.replace(f"__PH_{idx}__", ph)
    return text


def load_po_sanitized(path: str) -> polib.POFile | None:
    """
    Load a .po file, sanitizing common issues if necessary.
    """
    try:
        return polib.pofile(path)
    except OSError:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        # fix malformed fuzzy flags
        text = re.sub(r"^#,(?!\s)", "#, ", text, flags=re.MULTILINE)
        # remove empty header entries
        parts = text.split("\n\n", 1)
        header = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        rest_clean = re.sub(
            r"^msgid \"\"\s*\nmsgstr \"\"\s*\n?", "",
            rest,
            flags=re.MULTILINE
        )
        sanitized = header + "\n\n" + rest_clean
        tmp = NamedTemporaryFile(mode="w+", delete=False, suffix=".po", encoding="utf-8")  # noqa: SIM115
        try:
            tmp.write(sanitized)
            tmp.flush()
            tmp.close()
            return polib.pofile(tmp.name)
        finally:
            try:
                os.unlink(tmp.name)
            except OSError as e:
                raise CommandError("Failed to write sanitized .po file") from e


class Command(BaseCommand):
    help = "Merge msgid/msgstr from en_GB PO into target-language POs via DeepL, preserving placeholders."

    def add_arguments(self, parser):
        parser.add_argument(
            "-l", "--language",
            dest="target_languages",
            action="append",
            required=True,
            metavar="LANG",
            help="Locale code for translation, e.g. de-DE, fr-FR."
        )
        parser.add_argument(
            "-a", "--app",
            dest="target_apps",
            action="append",
            required=True,
            metavar="APP",
            help="App label for translation, e.g. core, payments."
        )

    def handle(self, *args, **options) -> None:
        target_langs: list[str] = options['target_languages']
        target_apps: set[str] = set(options['target_apps'])
        auth_key = os.environ.get('DEEPL_AUTH_KEY')
        if not auth_key:
            raise CommandError('DEEPL_AUTH_KEY not set')

        for target_lang in target_langs:
            api_code = DEEPL_TARGET_LANGUAGES_MAPPING.get(target_lang)
            if not api_code:
                self.stdout.write(self.style.WARNING(f"Unknown language '{target_lang}'"))
                continue
            if api_code == 'unsupported':
                self.stdout.write(self.style.WARNING(f"Unsupported language '{target_lang}'"))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"→ Translating into {target_lang}"))

            for app_conf in apps.get_app_configs():
                if app_conf.label not in target_apps:
                    continue

                en_path = os.path.join(app_conf.path, 'locale', 'en_GB', 'LC_MESSAGES', 'django.po')
                if not os.path.isfile(en_path):
                    self.stdout.write(self.style.WARNING(f"• {app_conf.label}: no en_GB PO"))
                    continue

                self.stdout.write(f"• {app_conf.label}: loading English PO…")
                en_po = load_po_sanitized(en_path)

                missing = [e for e in en_po if e.msgid and not e.msgstr and not e.obsolete]
                if missing:
                    self.stdout.write(self.style.NOTICE(f"⚠️ {len(missing)} missing in en_GB"))
                    for e in missing:
                        input_msgstr = input(f"Enter translation for '{e.msgid}': ").strip()
                        if input_msgstr:
                            e.msgstr = input_msgstr
                        else:
                            e.msgstr = e.msgid
                    en_po.save(en_path)
                    self.stdout.write(self.style.SUCCESS("Updated en_GB PO"))

                entries = [e for e in en_po if e.msgid and not e.obsolete]
                source_map = {e.msgid: e.msgstr for e in entries}

                tgt_dir = os.path.join(app_conf.path, 'locale', target_lang.replace('-', '_'), 'LC_MESSAGES')
                os.makedirs(tgt_dir, exist_ok=True)
                tgt_path = os.path.join(tgt_dir, 'django.po')

                old_tgt = None
                if os.path.exists(tgt_path):
                    self.stdout.write(f"  loading existing {target_lang} PO…")
                    try:
                        old_tgt = load_po_sanitized(tgt_path)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Existing PO parse error({e!s}), starting fresh"))

                new_po = polib.POFile()
                new_po.metadata = en_po.metadata.copy()
                new_po.metadata['Language'] = target_lang

                for e in entries:
                    prev = old_tgt.find(e.msgid) if old_tgt else None
                    new_po.append(polib.POEntry(
                        msgid=e.msgid,
                        msgstr=prev.msgstr if prev and prev.msgstr else '',
                        msgctxt=e.msgctxt,
                        comment=e.comment,
                        tcomment=e.tcomment,
                        occurrences=e.occurrences,
                        flags=e.flags,
                    ))

                to_trans = [e for e in new_po if not e.msgstr]
                if not to_trans:
                    self.stdout.write(self.style.WARNING(f"All done for {app_conf.label}"))
                    continue

                protected = []
                maps: list[list[str]] = []
                for e in to_trans:
                    txt = source_map[e.msgid]
                    p_txt, p_map = placeholderize(txt)
                    protected.append(p_txt)
                    maps.append(p_map)

                data = [
                           ('auth_key', auth_key),
                           ('target_lang', api_code),
                       ] + [('text', t) for t in protected]
                resp = requests.post('https://api-free.deepl.com/v2/translate', data=data)
                try:
                    resp.raise_for_status()
                    result = resp.json()
                except Exception as exc:
                    raise CommandError(f"DeepL error: {exc} – {resp.text}")

                trans = result.get('translations', [])
                if len(trans) != len(to_trans):
                    raise CommandError(f"Got {len(trans)} translations, expected {len(to_trans)}")

                for e, obj, pmap in zip(to_trans, trans, maps):
                    e.msgstr = deplaceholderize(obj['text'], pmap)

                new_po.save(tgt_path)
                self.stdout.write(self.style.SUCCESS(f"Saved {tgt_path}"))

        self.stdout.write(self.style.SUCCESS("Done."))
