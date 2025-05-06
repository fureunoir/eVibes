import contextlib
import os
import re
from tempfile import NamedTemporaryFile

import polib
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

# Patterns to identify placeholders
PLACEHOLDER_REGEXES = [
    re.compile(r"\{[^}]+\}"),       # {name}, {type(instance)!s}, etc.
    re.compile(r"%\([^)]+\)[sd]"),  # %(verbose_name)s, %(count)d
]

def extract_placeholders(text: str) -> set[str]:
    """
    Extract all placeholders from given text.
    """
    phs: list[str] = []
    for rx in PLACEHOLDER_REGEXES:
        phs.extend(rx.findall(text))
    return set(phs)


def load_po_sanitized(path: str) -> polib.POFile:
    """
    Load a .po file via polib, sanitizing on parse errors.
    Raises CommandError if still unparsable.
    """
    try:
        return polib.pofile(path)
    except Exception:
        # read raw text
        try:
            with open(path, encoding='utf-8') as f:
                text = f.read()
        except OSError as e:
            raise CommandError(f"{path}: cannot read file ({e})")
        # fix fuzzy flags and empty header entries
        text = re.sub(r"^#,(?!\s)", "#, ", text, flags=re.MULTILINE)
        parts = text.split("\n\n", 1)
        header = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        rest = re.sub(r"^msgid \"\"\s*\nmsgstr \"\"\s*\n?", '', rest, flags=re.MULTILINE)
        sanitized = header + "\n\n" + rest
        tmp = NamedTemporaryFile(mode='w+', delete=False, suffix='.po', encoding='utf-8')  # noqa: SIM115
        try:
            tmp.write(sanitized)
            tmp.flush()
            tmp.close()
            return polib.pofile(tmp.name)
        except Exception as e:
            raise CommandError(f"{path}: syntax error after sanitization ({e})")
        finally:
            with contextlib.suppress(OSError):
                os.unlink(tmp.name)

class Command(BaseCommand):
    help = (
        "Scan target-language .po files and report any placeholder mismatches, grouped by app."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '-l', '--language',
            dest='target_languages',
            action='append',
            required=True,
            metavar='LANG',
            help='Locale code(s) to scan, e.g. de-DE, fr-FR'
        )
        parser.add_argument(
            '-a', '--app',
            dest='target_apps',
            action='append',
            required=True,
            metavar='APP',
            help='App label(s) to scan, e.g. core, geo'
        )
        parser.add_argument(
            '-p', '--path',
            dest='root_path',
            required=False,
            metavar='ROOT_PATH',
            help='Root path prefix to adjust file links'
        )

    def handle(self, *args, **options) -> None:
        langs: list[str] = options['target_languages']
        apps_to_scan: set[str] = set(options['target_apps'])
        root_path: str = options.get('root_path') or '/app/'

        for app_conf in apps.get_app_configs():
            if app_conf.label not in apps_to_scan:
                continue

            # Collect issues per app across all languages
            app_issues: list[str] = []

            for lang in langs:
                loc = lang.replace('-', '_')
                po_path = os.path.join(
                    app_conf.path, 'locale', loc, 'LC_MESSAGES', 'django.po'
                )
                if not os.path.exists(po_path):
                    continue

                try:
                    po = load_po_sanitized(po_path)
                except CommandError:
                    continue

                # Collect lines for this language
                lang_issues: list[str] = []
                for entry in po:
                    if not entry.msgid or not entry.msgstr or entry.obsolete:
                        continue
                    src_ph = extract_placeholders(entry.msgid)
                    dst_ph = extract_placeholders(entry.msgstr)
                    missing = src_ph - dst_ph
                    extra = dst_ph - src_ph
                    if missing or extra:
                        line_no = entry.linenum or '?'
                        display = po_path.replace('/app/', root_path)
                        if '\\' in root_path:
                            display = display.replace('/', '\\')
                        lang_issues.append(
                            f"    {display}:{line_no}: missing={sorted(missing)} extra={sorted(extra)}"
                        )

                if lang_issues:
                    # Header for language with issues
                    app_issues.append(f"  ► {lang}")
                    app_issues.extend(lang_issues)

            # Output per app
            if app_issues:
                self.stdout.write(f"→ App: {app_conf.label}")
                for line in app_issues:
                    self.stdout.write(line)
                self.stdout.write("")
            else:
                # No issues in any language for this app
                self.stdout.write(
                    self.style.SUCCESS(f"App {app_conf.label} has no placeholder issues.")
                )
                self.stdout.write("")

        self.stdout.write(self.style.SUCCESS("Done scanning."))
