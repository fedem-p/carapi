"""Configuration settings for the scraper and email notifications."""

from dataclasses import dataclass, field
from typing import Dict, Any
import os
import json
from dotenv import (  # type: ignore[import-not-found] # pylint: disable=import-error
    load_dotenv,
)

# Load environment variables from .env
load_dotenv()

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.json")


def load_settings():
    """Load settings from the settings.json file."""
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings):
    """Save settings to the settings.json file."""
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# Mappings for user-friendly labels <-> codes
BODY_TYPE_MAP = {
    "Compact": "1",
    "Convertible": "2",
    "Coupe": "3",
    "SUV": "4",
    "Station Wagon": "5",
    "Sedan": "6",
}
BODY_TYPE_MAP_REV = {v: k for k, v in BODY_TYPE_MAP.items()}
FUEL_MAP = {
    "Hybrid": "2",
    "Hybrid/Diesel": "3",
    "Gasoline": "B",
    "Diesel": "D",
}
FUEL_MAP_REV = {v: k for k, v in FUEL_MAP.items()}
SORT_OPTIONS = ["standard", "price", "age"]
SORT_LABELS = {"standard": "Standard", "price": "Price", "age": "Age"}
SORT_LABELS_REV = {v: k for k, v in SORT_LABELS.items()}


@dataclass
class Config:
    """Class for managing configuration settings for the scraper and email notifications."""

    base_url: str = "https://www.autoscout24.com/lst"  # Default URL set to .de
    filters: Dict[str, Any] = field(default_factory=dict)
    num_pages: int = 10
    scoring_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    excluded_cars: Dict[str, list] = field(default_factory=dict)
    email_settings = {
        "smtp_server": os.getenv("SMTP_SERVER"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD"),
        "recipient": os.getenv("EMAIL_RECIPIENT"),
    }

    def __post_init__(self):
        """Load settings from file and initialize config attributes."""
        settings = load_settings()
        self.filters = settings.get("filters", {})
        self.num_pages = settings.get("num_pages", 10)
        self.scoring_profiles = settings.get("scoring_profiles", {})
        self.excluded_cars = settings.get("excluded_cars", {})

    def save(self):
        """Save the current configuration to the settings file."""
        settings = {
            "filters": self.filters,
            "num_pages": self.num_pages,
            "scoring_profiles": self.scoring_profiles,
            "excluded_cars": self.excluded_cars,
        }
        save_settings(settings)

    def get_filters_for_frontend(self):
        """Return filters with user-friendly labels for the frontend."""
        f = self.filters.copy()
        # Map codes to labels for frontend
        f["body"] = [BODY_TYPE_MAP_REV.get(x, x) for x in f.get("body", [])]
        f["fuel"] = [FUEL_MAP_REV.get(x, x) for x in f.get("fuel", [])]
        f["sort"] = f.get("sort", "standard")  # Return code, not label
        # min_power: convert kW to HP for frontend
        try:
            min_power_kw = float(f.get("min_power", 0))
            f["min_power"] = str(round(min_power_kw * 1.341022))
        except (ValueError, TypeError):
            f["min_power"] = ""
        return f

    def set_filters_from_frontend(self, f):
        """Convert frontend filter labels to backend codes."""
        filters = f.copy()
        filters["body"] = [BODY_TYPE_MAP.get(x, x) for x in f.get("body", [])]
        filters["fuel"] = [FUEL_MAP.get(x, x) for x in f.get("fuel", [])]
        filters["sort"] = f.get("sort", "standard")
        # min_power: convert HP to kW for backend
        try:
            min_power_hp = float(f.get("min_power", 0))
            filters["min_power"] = str(round(min_power_hp / 1.341022))
        except (ValueError, TypeError):
            filters["min_power"] = ""
        return filters
