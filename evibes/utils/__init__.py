from evibes.settings import LANGUAGE_CODE, LANGUAGES


def get_language_from_header(accept_language):
    language_codes = {lang.split("-")[0]: lang for lang, _ in LANGUAGES}
    languages_dict = dict(LANGUAGES)

    if not accept_language:
        return LANGUAGE_CODE.lower()

    for lang in accept_language.split(","):
        lang_code_parts = lang.split(";")[0].strip().lower()

        if "-" in lang_code_parts:
            primary, country = lang_code_parts.split("-")
            lang_code_parts = f"{primary.lower()}-{country.upper()}"

        if lang_code_parts in languages_dict:
            return lang_code_parts

        primary_lang = lang_code_parts.split("-")[0]
        if primary_lang in language_codes:
            return language_codes[primary_lang].lower()

    return LANGUAGE_CODE.lower()
