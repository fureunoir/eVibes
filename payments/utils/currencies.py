import requests
from constance import config
from django.core.cache import cache


def update_currencies_to_euro(currency, amount):
    rates = cache.get("rates", None)

    if not rates:
        response = requests.get(f"https://rates.icoadm.in/api/v1/rates?key={config.EXCHANGE_RATE_API_KEY}")
        rates = response.json().get("rates")
        cache.set("rates", rates, 60 * 60 * 24)

    usd_to_eur = rates.get("eur")

    return float(amount) * float(rates.get(currency.lower(), 1)) / float(usd_to_eur)
