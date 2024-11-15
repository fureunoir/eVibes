import json

import requests
from constance import config


def update_currencies_to_euro(currency, amount):
    response = requests.get(f'https://rates.icoadm.in/api/v1/rates?key={config.EXCHANGE_RATE_API_KEY}')
    rates = json.loads(response.text)['rates']

    usd_to_eur = rates['eur']

    return float(amount) * float(rates[currency]) * float(usd_to_eur)
