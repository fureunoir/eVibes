import requests

from evibes.settings import GEONAMES_USERNAME


def perform_search(path, params):
    url = f"http://api.geonames.org/{path}"
    params.update({"username": GEONAMES_USERNAME, "maxRows": 5})
    response = requests.get(url, params=params)
    try:
        json_response = response.json()
        return response.status_code, json_response
    except ValueError:
        print('Decoding JSON has failed:', response.content)
        return response.status_code, {}


def get_country_iso_code(country_name):
    status_code, res = perform_search(path="searchJSON", params={"q": country_name, "featureClass": "A"})

    if status_code == 200:
        for result in res.get("geonames", []):
            if result.get("countryName") == country_name:
                return result.get("countryCode")
