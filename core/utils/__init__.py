from django.utils.crypto import get_random_string


def get_random_code() -> str:
    return get_random_string(20)
