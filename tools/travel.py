import json
from pathlib import Path
from typing import Any

from config import settings


def check_demo_travel(destination: str | None = None) -> dict[str, Any]:
    path = Path(settings.travel_data_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path

    if not path.exists():
        return {
            "found": False,
            "message": f"Travel demo file not found at {path}. Set TRAVEL_DATA_PATH or create demo_travel.json.",
        }

    data = json.loads(path.read_text(encoding="utf-8"))
    trips = data.get("trips", [])
    if destination:
        needle = destination.lower()
        trips = [
            trip
            for trip in trips
            if needle in trip.get("destination", "").lower() or needle in trip.get("name", "").lower()
        ]

    return {"found": bool(trips), "trips": trips}
