from core.utils.lists import BAD_KEYS_TO_LISTEN


def is_safe_key(attr: str) -> bool:
    return attr not in BAD_KEYS_TO_LISTEN
