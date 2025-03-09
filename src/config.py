"""config docstring."""

from dataclasses import dataclass, field
from typing import Dict, Any
from .fetch_makes_and_models import FILTER_MAKES


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
            "sort": "standard",
            "brands": FILTER_MAKES,
        }
    )
    email_settings: Dict[str, str] = field(
        default_factory=lambda: {
            "smtp_server": "smtp.example.com",
            "smtp_port": "587",
            "username": "your_email@example.com",
            "password": "your_password",
            "recipient": "recipient@example.com",
        }
    )
    num_pages: int = 2  # Default number of pages to scrape
