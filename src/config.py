"""Configuration settings for the scraper and email notifications."""

from dataclasses import dataclass, field
from typing import Dict, Any
import os
from dotenv import (  # type: ignore[import-not-found] # pylint: disable=import-error
    load_dotenv,
)
from src.fetch_makes_and_models import FILTER_MAKES

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
    num_pages: int = 10  # Default number of pages to scrape
    # Scoring profiles: adjust weights and criteria per profile
    scoring_profiles: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "standard": {
                "weights": {
                    "price": 4.5,
                    "mileage": 3,
                    "fuel_type": 3,
                    "features": 3,
                    "adaptive_cruise": 2,
                    "power": 1,
                    "registration_year": 3,
                    "body_type": 2,
                    "emissions": 3,
                    "coolness_factor": 2,
                    "warranty": 3,
                    "seat_heating": 2,
                },
                "fuel_scores": {
                    "electric/diesel": 1.0,
                    "electric/gasoline": 0.9,
                    "diesel": 0.8,
                    "gasoline": 0.7,
                    "super 95": 0.7,
                    "regular/benzine 91": 0.7,
                },
                "favorite_models": [
                    ("skoda", "superb"),
                    ("skoda", "octavia"),
                    ("skoda", "kamiq"),
                    ("audi", "x"),
                    ("seat", "ateca"),
                    ("cupra", "x"),
                    ("bmw", "x"),
                    ("ford", "explorer"),
                    ("jaguar", "x"),
                    ("lexus", "x"),
                    ("maserati", "x"),
                    ("mazda", "6"),
                    ("mercedes-benz", "x"),
                    ("porsche", "x"),
                    ("toyota", "rav 4"),
                    ("toyota", "camry"),
                    ("toyota", "prius"),
                    ("toyota", "yaris cross"),
                    ("volkswagen", "arteon"),
                    ("volkswagen", "tiguan"),
                    ("volkswagen", "golf gti"),
                ],
            },
            # Add more profiles as needed
        }
    )
    excluded_cars: Dict[str, list] = field(
        default_factory=lambda: {
            "volkswagen": ["caddy", "taigo"],
            "opel": [
                "astra",
                "corsa",
                "grandland x",
                "grandland",
                "crossland x",
                "crossland",
                "mokka",
            ],
            "ford": ["puma", "fiesta"],
            "skoda": ["scala", "fabia"],
            "hyundai": ["kona", "i20", "nexo"],
            "toyota": ["c-hr"],
            "bmw": ["118"],
            "peugeot": ["208", "308"],
            "nissan": ["micra", "juke"],
            "renault": ["zoe", "clio"],
            "citroen": ["c3"],
            "kia": ["rio", "niro"],
            "dacia": ["logan", "sandero"],
            "seat": ["ibiza"],
        }
    )
