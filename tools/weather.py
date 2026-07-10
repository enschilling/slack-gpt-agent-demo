from typing import Any

import requests


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


def _parse_us_location(location: str) -> tuple[str, str | None]:
    parts = [part.strip() for part in location.split(",") if part.strip()]
    if len(parts) < 2:
        return location.strip(), None

    state = parts[1].upper()
    return parts[0], US_STATES.get(state, parts[1])


def _choose_place(results: list[dict[str, Any]], state: str | None) -> dict[str, Any] | None:
    if not results:
        return None

    us_results = [place for place in results if place.get("country_code") == "US"]
    candidates = us_results or results
    if state:
        state_lower = state.lower()
        for place in candidates:
            if (place.get("admin1") or "").lower() == state_lower:
                return place

    return candidates[0]


def get_weather_forecast(location: str, days: int = 3) -> dict[str, Any]:
    days = max(1, min(days, 7))
    search_name, state = _parse_us_location(location)
    geo = requests.get(
        GEOCODE_URL,
        params={"name": search_name, "count": 10, "language": "en", "format": "json"},
        timeout=20,
    )
    geo.raise_for_status()
    results = geo.json().get("results") or []
    place = _choose_place(results, state)
    if not place:
        return {"found": False, "message": f"No weather location found for {location}."}

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
