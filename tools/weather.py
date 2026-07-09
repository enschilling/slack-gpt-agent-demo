from typing import Any

import requests


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_forecast(location: str, days: int = 3) -> dict[str, Any]:
    days = max(1, min(days, 7))
    geo = requests.get(
        GEOCODE_URL,
        params={"name": location, "count": 1, "language": "en", "format": "json"},
        timeout=20,
    )
    geo.raise_for_status()
    results = geo.json().get("results") or []
    if not results:
        return {"found": False, "message": f"No weather location found for {location}."}

    place = results[0]
    forecast = requests.get(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "temperature_unit": "fahrenheit",
            "timezone": "auto",
            "forecast_days": days,
        },
        timeout=20,
    )
    forecast.raise_for_status()
    daily = forecast.json()["daily"]

    return {
        "found": True,
        "location": {
            "name": place.get("name"),
            "region": place.get("admin1"),
            "country": place.get("country"),
        },
        "forecast": [
            {
                "date": daily["time"][index],
                "high_f": daily["temperature_2m_max"][index],
                "low_f": daily["temperature_2m_min"][index],
                "precipitation_probability_percent": daily["precipitation_probability_max"][index],
            }
            for index in range(len(daily["time"]))
        ],
    }
