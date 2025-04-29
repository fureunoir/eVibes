from django.utils.translation import gettext_lazy as _

from payments.utils.cbr import get_rates as get_rates_cbr


def get_rates(provider: str):
    if not provider:
        raise ValueError(_("a provider to get rates from is required"))

    match provider:
        case "cbr":
            return get_rates_cbr()
        case _:
            raise ValueError(_(f"couldn't find provider {provider}"))
