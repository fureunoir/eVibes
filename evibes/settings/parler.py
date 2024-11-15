PARLER_LANGUAGES = {
    None: (
        {'code': 'en-gb', 'name': 'English'},
        {'code': 'ru-ru', 'name': 'Russian'},
        {'code': 'de-de', 'name': 'German'},
        {'code': 'it-it', 'name': 'Italian'},
        {'code': 'es-es', 'name': 'Spanish'},
        {'code': 'nl-nl', 'name': 'Dutch'},
        {'code': 'fr-fr', 'name': 'French'},
        {'code': 'ro-ro', 'name': 'Romanian'},
        {'code': 'pl-pl', 'name': 'Polish'},
        {'code': 'cs-cz', 'name': 'Czech'},
        {'code': 'da-dk', 'name': 'Danish'},
    ),
    'default': {
        'fallbacks': ['ru-ru'],
        'hide_untranslated': False,
    },
}

PARLER_DEFAULT_LANGUAGE_CODE = 'ru-ru'