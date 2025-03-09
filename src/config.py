"""config docstring."""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Config:
    """Class for managing configuration settings for the scraper and email notifications."""

    base_url: str = "https://www.autoscout24.de"  # Default URL set to .de
    filters: Dict[str, Any] = field(
        default_factory=lambda: {
            "make": "Toyota",
            "model": "Corolla",
            "min_price": 5000,
            "max_price": 20000,
            "min_year": 2015,
            "max_year": 2022,
            "country": "DE",
            "brands": ["Toyota", "Honda", "Ford"],
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
    num_pages: int = 5  # Default number of pages to scrape
