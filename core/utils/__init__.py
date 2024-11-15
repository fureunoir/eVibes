import requests
from constance import config
from django.utils.crypto import get_random_string


def get_random_code() -> str:
    return get_random_string(20)


def get_amount_from_currency(amount: float, currency: str):
    if currency.lower() == 'eur':  # Ensuring case-insensitivity
        return amount

    try:
        response = requests.get(f'https://rates.icoadm.in/api/v1/rates?key={config.EXCHANGE_RATE_API_KEY}')
        response.raise_for_status()  # Raise an HTTPError for bad requests (4xx or 5xx)
        rates = response.json().get('rates', {})

        if not rates:
            raise ValueError("No rates data found in the response")

        euro_rate = float(rates.get('eur', 1.0))  # default to 1.0 if not found
        target_rate = float(rates.get(currency.lower(), 1.0))  # default to 1.0 if not found
        converted_amount = amount / round(target_rate * euro_rate, 2)
        return round(converted_amount, 2)

    except requests.RequestException as e:
        raise SystemError(f"Request to currency exchange API failed: {e}")
    except ValueError as e:
        raise ValueError(f"Error processing exchange rates: {e}")
    except KeyError as e:
        raise KeyError(f"Currency '{currency}' not found in rates")
    except Exception as e:
        raise SystemError(f"An unexpected error occurred: {e}")


def get_product_uuid_as_path(instance, filename):
    return str(instance.product.uuid) + '/' + filename
