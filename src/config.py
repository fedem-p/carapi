"""Configuration settings for the scraper and email notifications."""

from dataclasses import dataclass, field
from typing import Dict, Any
import os
from dotenv import (  # type: ignore[import-not-found] # pylint: disable=import-error
    load_dotenv,
)
from .fetch_makes_and_models import FILTER_MAKES

# Load environment variables from .env
load_dotenv()


@dataclass
class Config:
    """Class for managing configuration settings for the scraper and email notifications."""

    base_url: str = "https://www.autoscout24.com/lst"  # Default URL set to .de
    filters: Dict[str, Any] = field(
        default_factory=lambda: {
            "body": ["2", "3", "4", "5", "6"],
            "custtype": "D",  # Customer type: dealer
            "country": "D",  # Country code
            "emclass": "5",
            "ensticker": "4",
            "eq": ["37"],
            "min_year": "2020",
            "kmto": "100000",
            "min_power": "74",
            "max_price": "20000",
            "min_seats": "4",
            "fuel": ["2", "3", "B", "D"],
            "sort": "standard",
            "brands": FILTER_MAKES,
        }
    )
    email_settings = {
        "smtp_server": os.getenv("SMTP_SERVER"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),  # Default to "587" as a string
        "username": os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD"),
        "recipient": os.getenv("EMAIL_RECIPIENT"),
    }
    num_pages: int = 2  # Default number of pages to scrape
