import json
from datetime import date
from pathlib import Path
from typing import Any

from config import settings


def _app_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def _configured_paths() -> list[Path]:
    configured = settings.travel_data_path.strip()
    legacy_default = not configured or configured == "demo_travel.json"

    if legacy_default:
        monthly_files = sorted(_app_dir().glob("demo_travel_*.json"))
        if monthly_files:
            return monthly_files

    raw_paths = [
        item.strip()
        for item in configured.replace(";", ",").split(",")
        if item.strip()
    ] or ["demo_travel.json"]

    paths = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = _app_dir() / path
        paths.append(path)

    return paths


def _load_trips(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    trips = data.get("trips", [])
    for trip in trips:
        trip.setdefault("source_file", path.name)
    return trips


def _month_name(value: str) -> str:
    try:
        return date.fromisoformat(value).strftime("%B")
    except ValueError:
        return ""


def _matches_trip(trip: dict[str, Any], query: str) -> bool:
    haystack = [
        trip.get("destination", ""),
        trip.get("name", ""),
        trip.get("source_file", ""),
        _month_name(trip.get("start_date", "")),
        _month_name(trip.get("end_date", "")),
    ]
    return query.lower() in " ".join(haystack).lower()


def check_demo_travel(destination: str | None = None) -> dict[str, Any]:
    paths = _configured_paths()
    trips = []
    for path in paths:
        trips.extend(_load_trips(path))

    if not trips:
        return {
            "found": False,
            "message": (
                "No demo travel files were found. Create demo_travel_july.json and "
                "demo_travel_august.json, or set TRAVEL_DATA_PATH to one or more JSON files."
            ),
        }

    if destination:
        trips = [trip for trip in trips if _matches_trip(trip, destination)]

    return {"found": bool(trips), "trips": trips, "source_files": [path.name for path in paths]}
