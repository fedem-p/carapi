"""Scraper module for fetching car data from Autoscout24."""

from datetime import datetime
import logging
import random
import time
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from src.constants import EXCLUDED_CARS
from src.fetch_makes_and_models import load_makes_from_csv

# Correct the import order
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperException(Exception):
    """Custom exception for scraper errors."""


class Scraper:
    """Scraper class for extracting car listings from Autoscout24."""

    def __init__(self, config):
        """Initialize the Scraper with configuration settings.

        Args:
            config (Config): An instance of the Config class containing settings for scraping.
        """
        self.config = config

    def scrape_data(self, sort_method="standard", progress_callback=None):
        """Scrape car data from the configured URL for the specified number of pages.

        Raises:
            ScraperException: If the request to the website fails or returns an error status.

        Returns:
            list: A list of dictionaries containing car data.
        """
        all_cars = []
        total_pages = self.config.num_pages
        for page in tqdm(
            range(1, total_pages + 1), desc="Scraping pages", unit="page"
        ):
            url = self._construct_url(page, sort_method)

            logger.debug("============= Scraping page %s =============", page)

            response = self._get_response(url)
            if response:
                cars = self._parse_cars_from_html(response.text)
                all_cars.extend(cars)

            if progress_callback:
                progress_callback(page, total_pages)

            wait_time = random.uniform(1, 3)
            logger.debug(
                "Waiting for %.2f seconds before the next request...", wait_time
            )
            logger.info(".")  # Print to display progress bar in docker logs
            time.sleep(wait_time)

        return all_cars

    def _get_response(self, url):
        """Helper method to send GET request and handle exceptions."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # This will raise an error for bad responses
            return response
        except requests.exceptions.Timeout as e:
            logger.error("Request to %s timed out: %s", url, e)
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred: %s", e)
        return None

    def _construct_url(self, page, sort_method):
        """Construct the search URL with query parameters based on the filters."""
        params = {
            "atype": "C",  # Example: Car type
            "body": ",".join(map(str, self.config.filters.get("body", []))),
            "custtype": self.config.filters.get("custtype", "D"),
            "cy": self.config.filters.get("country", "D"),
            "desc": 0,
            "emclass": self.config.filters.get("emclass", ""),
            "ensticker": self.config.filters.get("ensticker", ""),
            "eq": ",".join(map(str, self.config.filters.get("eq", []))),
            "fregfrom": self.config.filters.get("min_year", ""),
            "kmto": self.config.filters.get("kmto", ""),
            "powerfrom": self.config.filters.get("min_power", ""),
            "powertype": "hp",
            "fuel": ",".join(map(str, self.config.filters.get("fuel", []))),
            "page": page,
            "priceto": self.config.filters.get("max_price", ""),
            "seatsfrom": self.config.filters.get("min_seats", ""),
            "sort": sort_method,
            "damaged_listing": "exclude",
            "ocs_listing": "include",
            "ustate": ",".join(self.config.filters.get("ustate", ["N", "U"])),
        }

        brands = self.config.filters.get("brands")
        if brands:
            all_brands = load_makes_from_csv()
            mmvm_parts = [f"{all_brands.get(b.lower())}|||" for b in brands]
            params["mmmv"] = ",".join(mmvm_parts)

        return f"{self.config.base_url}/search?" + urlencode(params)

    def _parse_cars_from_html(self, html):
        """Parse HTML and extract car data."""
        soup = BeautifulSoup(html, "html.parser")
        return self.extract_car_data(soup)

    def extract_car_data(self, soup):
        """Extract relevant car data from the parsed HTML."""
        car_list = []
        listings = soup.find_all("article", class_="cldt-summary-full-item")

        if not listings:
            logger.warning("No car listings found on this page.")
            return car_list

        for car in listings:
            car_data = self._extract_car_details(car)
            if car_data:
                car_list.append(car_data)

        return car_list

    def _filter_car(self, car_make, car_model):
        """Return True if the car should be excluded based on make/model or other rules."""
        if car_make in EXCLUDED_CARS and car_model in EXCLUDED_CARS[car_make]:
            logger.debug("Skipped %s | %s", car_make, car_model)
            return True
        # Add more filtering rules here as needed
        return False

    def _clean_car_data(self, car_data):
        """Normalize and clean car data fields."""
        # Normalize price
        if car_data.get("price") is not None:
            if isinstance(car_data["price"], str):
                try:
                    car_data["price"] = self._parse_price(car_data["price"])
                except (ValueError, TypeError):
                    car_data["price"] = None
        # Normalize mileage
        if car_data.get("mileage") is not None:
            if isinstance(car_data["mileage"], str):
                try:
                    car_data["mileage"] = self._parse_km(car_data["mileage"])
                except (ValueError, TypeError):
                    car_data["mileage"] = None
        # Normalize year
        if car_data.get("year") is not None:
            try:
                car_data["year"] = int(car_data["year"])
            except (ValueError, TypeError):
                car_data["year"] = None
        # Add more normalization as needed
        return car_data

    def _extract_car_details(self, car):
        """Helper method to extract car details from a single listing."""
        try:
            url = car.find("a", class_="ListItem_title__ndA4s")["href"]
            full_url = f"https://www.autoscout24.com{url}"
            car_make = car.get("data-make", "").strip()
            car_model = car.get("data-model", "").strip()
            car_price = self._parse_price(car.get("data-price"))
            car_km = self._parse_km(car.get("data-mileage"))
            car_year = self._parse_year(car.get("data-first-registration"))

            if self._filter_car(car_make, car_model):
                return None

            # Scrape additional details and update the car data
            car_data = self.scrape_car_details(full_url)
            if car_data:
                car_data.update(
                    {
                        "url": full_url,
                        "make": car_make,
                        "model": car_model,
                        "year": car_year,
                        "price": car_price,
                        "mileage": car_km,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                car_data = self._clean_car_data(car_data)
                logger.debug(
                    "Scraped new car: %s | %s | %s euro | %skm",
                    car_make,
                    car_model,
                    car_price,
                    car_km,
                )
                return car_data

        except (AttributeError, ValueError, IndexError, ScraperException) as e:
            logger.error("Error extracting data for a car: %s", e)

        return None

    def _parse_price(self, price_str):
        """Helper method to parse the car price."""
        if price_str:
            return int(price_str.replace("€", "").replace(".", "").strip())
        return None

    def _parse_km(self, km_str):
        """Helper method to parse mileage."""
        if km_str:
            return int(km_str.replace("km", "").replace(",", "").strip())
        return None

    def _parse_year(self, year_str):
        """Helper method to parse the car year."""
        if year_str:
            return int(year_str.split("-")[1])
        return None

    def scrape_car_details(self, url):
        """Scrape additional details from the car's individual listing page."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            details_mapping = {
                "Body type": "body_type",
                "Type": "car_type",
                "Seats": "seats",
                "Doors": "doors",
                "Country version": "country_version",
                "Offer number": "offer_number",
                "Warranty": "warranty",
                "Mileage": "vehicle_mileage",
                "First registration": "first_registration",
                "General inspection": "general_inspection",
                "Previous owner": "previous_owner",
                "Full service history": "full_service_history",
                "Non-smoker vehicle": "non_smoker_vehicle",
                "Power": "power",
                "Gearbox": "gearbox",
                "Engine size": "engine_size",
                "Emission class": "emission_class",
                "Emissions sticker": "emission_sticker",
                "Fuel type": "fuel_type",
            }

            additional_details = {key: None for key in details_mapping.values()}
            additional_details.update(
                {
                    "android_auto": False,
                    "car_play": False,
                    "cruise_control": False,
                    "adaptive_cruise_control": False,
                    "seat_heating": False,
                    "img_url": None,
                }
            )

            self._extract_details(soup, details_mapping, additional_details)

            return additional_details

        except requests.exceptions.RequestException as e:
            raise ScraperException(f"Error fetching details from {url}: {e}") from e

    def _extract_details(self, soup, details_mapping, additional_details):
        """Helper method to extract details from sections."""

        def extract_details(section_id):
            section = soup.find("section", id=section_id)
            if section:
                for detail in section.find_all(
                    "dl", class_="DataGrid_defaultDlStyle__xlLi_"
                ):
                    for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                        key = dt.text.strip()
                        if key in details_mapping:
                            value = dd.text.strip()
                            if key in ["Seats", "Doors", "Previous owner"]:
                                additional_details[details_mapping[key]] = int(value)
                            elif key == "Mileage":
                                additional_details["vehicle_mileage"] = int(
                                    value.replace(" km", "").replace(",", "").strip()
                                )
                            else:
                                additional_details[details_mapping[key]] = value

        extract_details("basic-details-section")
        extract_details("listing-history-section")
        extract_details("technical-details-section")
        extract_details("environment-details-section")
        self._extract_equipment_details(soup, additional_details)

    def _extract_equipment_details(
        self, soup, additional_details
    ):  # pylint: disable=too-many-branches
        """Extract equipment details from the equipment section."""
        equipment_section = soup.find("section", id="equipment-section")
        if equipment_section:  # pylint: disable=too-many-nested-blocks
            for detail in equipment_section.find_all(
                "dl", class_="DataGrid_defaultDlStyle__xlLi_"
            ):
                for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                    if dt.text.strip() == "Comfort & Convenience":
                        for item in dd.find_all("li"):
                            if "Android Auto" in item.text:
                                additional_details["android_auto"] = True
                            if "Apple CarPlay" in item.text:
                                additional_details["car_play"] = True
                            if "Seat heating" in item.text:
                                additional_details["seat_heating"] = True
                    elif dt.text.strip() == "Safety & Security":
                        for item in dd.find_all("li"):
                            if "Cruise Control" in item.text:
                                additional_details["cruise_control"] = True
                            if "Adaptive Cruise Control" in item.text:
                                additional_details["adaptive_cruise_control"] = True

        # Extract image URL
        image_gallery_div = soup.find("div", class_="image-gallery-slides")
        if image_gallery_div:
            sources = image_gallery_div.find_all("source")
            for source in sources:
                if source.get("type") == "image/jpeg":
                    additional_details["img_url"] = source.get("srcset")
                    break  # Stop after finding the first JPEG
