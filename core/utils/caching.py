import json
import logging
from pathlib import Path

from django.core.cache import cache
from django.core.exceptions import BadRequest
from django.utils.translation import gettext_lazy as _

from evibes.settings import UNSAFE_CACHE_KEYS
from vibes_auth.models import User

logger = logging.getLogger(__name__)


def is_safe_cache_key(key: str):
    return key not in UNSAFE_CACHE_KEYS


def get_cached_value(user: User, key: str, default=None) -> None | object:
    if user.is_staff or user.is_superuser:
        return cache.get(key, default)

    if is_safe_cache_key(key):
        return cache.get(key, default)

    return None


def set_cached_value(user: User, key: str, value: object, timeout: int = 3600) -> None | object:
    if user.is_staff or user.is_superuser:
        cache.set(key, value, timeout)
        return value

    return None


def web_cache(request, key, data, timeout):
    if not data and not timeout:
        return {"data": get_cached_value(request.user, key)}
    if (data and not timeout) or (timeout and not data):
        raise BadRequest(_("both data and timeout are required"))
    if not 0 < int(timeout) < 216000:
        raise BadRequest(_("invalid timeout value, it must be between 0 and 216000 seconds"))
    return {"data": set_cached_value(request.user, key, data, timeout)}


def set_default_cache():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    for json_file in data_dir.glob("*.json"):
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Setting cache for {json_file.stem}")
        cache.set(json_file.stem, data, timeout=28800)
