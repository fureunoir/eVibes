import requests
from constance import config
from django.contrib.gis.geos import Point
from django.db import models


class AddressManager(models.Manager):
    def create(self, raw_data: str, **kwargs):
        """
        Create an Address instance by geocoding the provided raw address string.

        Args:
            raw_data (str): The raw address input from the user (e.g., '36 Mornington Rd Loughton England').
            **kwargs: Additional fields to pass to the Address model (e.g., user).
        """
        if not raw_data:
            raise ValueError("'raw_data' (address string) must be provided.")

        # Query Nominatim
        params = {
            "format": "json",
            "addressdetails": 1,
            "q": raw_data,
        }
        resp = requests.get(config.NOMINATIM_URL.rstrip("/") + "/search", params=params)
        resp.raise_for_status()
        results = resp.json()
        if not results:
            raise ValueError(f"No geocoding result for address: {raw_data}")
        data = results[0]

        # Parse address components
        addr = data.get("address", {})
        street = addr.get("road") or addr.get("pedestrian") or ""
        district = addr.get("city_district") or addr.get("suburb") or ""
        city = addr.get("city") or addr.get("town") or addr.get("village") or ""
        region = addr.get("state") or addr.get("region") or ""
        postal_code = addr.get("postcode") or ""
        country = addr.get("country") or ""

        # Parse location
        try:
            lat = float(data.get("lat"))
            lon = float(data.get("lon"))
            location = Point(lon, lat, srid=4326)
        except (TypeError, ValueError):
            location = None

        # Create the model instance, storing both the input string and full API response
        return super().create(
            raw_data=raw_data,
            street=street,
            district=district,
            city=city,
            region=region,
            postal_code=postal_code,
            country=country,
            location=location,
            api_response=data,
            **kwargs,
        )
