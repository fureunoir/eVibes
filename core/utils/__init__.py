import logging
import re
import secrets
from contextlib import contextmanager

from constance import config
from django.core.cache import cache
from django.db import transaction
from django.utils.crypto import get_random_string

from evibes.settings import DEBUG, EXPOSABLE_KEYS, LANGUAGE_CODE

logger = logging.getLogger(__name__)


def get_random_code() -> str:
    """
    Generates a random string of a specified length. This method utilizes the
    get_random_string function to create a random alphanumeric string of
    20 characters in length.

    Returns
    -------
    str
        A 20-character-long alphanumeric string.
    """
    return get_random_string(20)


def get_product_uuid_as_path(instance, filename):
    """
    Generates a unique file path for a product using its UUID.

    This function constructs a file path that includes the product UUID
    in its directory structure. The path format is "products/{product_uuid}/{filename}",
    where `product_uuid` is derived from the instance's product attribute, and
    `filename` corresponds to the original name of the file being processed.

    Parameters:
    instance: Object
        The model instance containing the product attribute with the desired UUID.
    filename: str
        The original name of the file for which the path is being generated.

    Returns:
    str
        A string representing the generated unique file path that adheres to the
        format "products/{product_uuid}/{filename}".
    """
    return "products" + "/" + str(instance.product.uuid) + "/" + filename


def get_brand_name_as_path(instance, filename):
    return "brands/" + str(instance.name) + "/" + filename


@contextmanager
def atomic_if_not_debug():
    """
    A context manager to execute a database operation within an atomic transaction
    when the `DEBUG` setting is disabled. If `DEBUG` is enabled, it bypasses
    transactional behavior. This allows safe rollback in production and easier
    debugging in development.

    Yields
    ------
    None
        Yields control to the enclosed block of code.
    """
    if not DEBUG:
        with transaction.atomic():
            yield
    else:
        yield


def is_url_safe(url: str) -> bool:
    """
    Determine if a given URL is safe. This function evaluates whether
    the provided URL starts with "https://", making it a potentially
    secure resource, by evaluating its prefix using a regular expression.

    Arguments:
        url (str): The URL to evaluate.

    Returns:
        bool: True if the URL starts with "https://", indicating it may
              be considered safe. False otherwise.
    """
    return bool(re.match(r"^https://", url, re.IGNORECASE))


def format_attributes(attributes: str | None = None):
    if not attributes:
        return {}

    try:
        attribute_pairs = attributes.split(",")
    except AttributeError:
        return {}

    result = {}
    for attr_pair in attribute_pairs:
        try:
            key, value = attr_pair.split("=")
            result[key] = value
        except ValueError:
            continue

    return result


def get_project_parameters():
    parameters = cache.get("parameters", {})

    if not parameters:
        for key in EXPOSABLE_KEYS:
            parameters[key.lower()] = getattr(config, key)

        cache.set("parameters", parameters, 60 * 60)

    return parameters


def resolve_translations_for_elasticsearch(instance, field_name):
    field = getattr(instance, f"{field_name}_{LANGUAGE_CODE}", "")
    filled_field = getattr(instance, field_name, "")
    if not field:
        setattr(instance, f"{field_name}_{LANGUAGE_CODE}", filled_field)


CROCKFORD = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_human_readable_id(length: int = 6) -> str:
    """
    Generate a human-readable ID of `length` characters (from the Crockford set),
    with a single hyphen inserted:
      - 50% chance at the exact middle
      - 50% chance at a random position between characters (1 to length-1)

    The final string length will be `length + 1` (including the hyphen).
    """
    chars = [secrets.choice(CROCKFORD) for _ in range(length)]

    pos = (secrets.randbelow(length - 1) + 1) if secrets.choice([True, False]) else (length // 2)

    chars.insert(pos, "-")
    return "".join(chars)
