import requests
from django.core.cache import cache
from sentry_sdk import capture_exception


def get_rates():
    try:
        rates = cache.get("cbr_rates", None)

        if not rates:
            response = requests.get("https://www.cbr-xml-daily.ru/latest.js")
            rates = response.json().get("rates")
            cache.set("cbr_rates", rates, 60 * 60 * 24)

        return rates

    except Exception as e:
        capture_exception(e)
        raise e
