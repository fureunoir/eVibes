from typing import Dict, List

import requests
from constance import config
from django.utils.translation import gettext as _


def fetch_address_suggestions(query: str, limit: int = 5) -> List[Dict]:
    if not config.NOMINATIM_URL:
        raise ValueError(_("NOMINATIM_URL must be configured."))

    url = config.NOMINATIM_URL.rstrip("/") + "/search"
    params = {
        "format": "json",
        "addressdetails": 1,
        "q": query,
        "limit": limit,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()

    suggestions = []
    for item in results:
        suggestions.append(
            {
                "display_name": item.get("display_name"),
                "lat": item.get("lat"),
                "lon": item.get("lon"),
                "address": item.get("address", {}),
            }
        )
    return suggestions
