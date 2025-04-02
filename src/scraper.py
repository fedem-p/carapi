"""Scraper module for fetching car data from Autoscout24."""

from datetime import datetime
import logging
import random
import time
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from .fetch_makes_and_models import load_makes_from_csv
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXCLUDED_CARS = {
    "volkswagen": ["caddy", "taigo"],
    "opel": ["astra", "corsa", "grandland x", "grandland", "crossland x", "crossland", "mokka"],
    "ford": ["puma", "fiesta"],
    "skoda": ["scala", "fabia"],
    "hyundai": ["kona", "i20", "nexo"],
    "toyota": ["c-hr"],
    "bmw": ["118"],
    "peugeot": ["208", "308"],
    "nissan": ["micra", "juke"],
    "renault": ["zoe"],
    "citroen": ["c3"],
    "kia": ["rio"],
    "dacia": ["logan", "sandero"],
    "seat": ["ibiza"],
}


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

    def scrape_data(self, sort_method="standard"):
        """Scrape car data from the configured URL for the specified number of pages.

        Raises:
            ScraperException: If the request to the website fails or returns an error status.

        Returns:
            list: A list of dictionaries containing car data.
        """
        all_cars = []
        for page in tqdm(
            range(1, self.config.num_pages + 1), desc="Scraping pages", unit="page"
        ):  # Loop through the specified number of pages
            url = self.construct_url(page, sort_method)

            logger.debug("============= Scraping page %s =============", page)

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # This will raise an error for bad responses
            except requests.exceptions.Timeout as e:
                raise ScraperException(f"Request to {url} timed out: {e}") from e
            except requests.exceptions.RequestException as e:
                raise ScraperException(f"An error occurred: {e}") from e
            if response.status_code == 200:
                # Parse the response using BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                cars = self.extract_car_data(soup)
                all_cars.extend(cars)  # Add the cars from this page to the overall list
            else:
                raise ScraperException(
                    f"Failed to fetch data from page {page}: Status code {response.status_code}"
                )

            wait_time = random.uniform(1, 3)
            logger.debug(
                "Waiting for %.2f seconds before the next request...", wait_time
            )
            # print to display progress bar though the docker logs
            logger.info(".")
            time.sleep(wait_time)

        return all_cars

    def construct_url(self, page, sort_method):
        """Construct the search URL with query parameters based on the filters.

        Args:
            page (int): The page number to fetch.

        Returns:
            str: The constructed URL for scraping car data.
        """
        # Build the URL with query parameters based on filters
        params = {
            "atype": "C",  # Example: Car type
            "body": ",".join(
                map(str, self.config.filters.get("body", []))
            ),  # Body types
            "custtype": self.config.filters.get("custtype", "D"),  # Customer type
            "cy": self.config.filters.get("country", "D"),  # Country code
            "desc": 0,  # Description flag
            "emclass": self.config.filters.get("emclass", ""),  # Emission class
            "ensticker": self.config.filters.get("ensticker", ""),  # Sticker type
            "eq": ",".join(
                map(str, self.config.filters.get("eq", []))
            ),  # Equipment type
            "fregfrom": self.config.filters.get(
                "min_year", ""
            ),  # From year of registration
            "kmto": self.config.filters.get("kmto", ""),  # Maximum kilometers driven
            "powerfrom": self.config.filters.get("min_power", ""),  # Minimum power
            "powertype": "hp",  # Power type
            "page": page,  # Add the page number to the parameters
            "priceto": self.config.filters.get("max_price", ""),  # Maximum price
            "seatsfrom": self.config.filters.get(
                "min_seats", ""
            ),  # Minimum number of seats
            "sort": sort_method,  # Sorting method
            "damaged_listing": "exclude",
            "ocs_listing": "include",
            "ustate": ",".join(
                self.config.filters.get("ustate", ["N", "U"])
            ),  # Vehicle condition
        }

        brands = self.config.filters.get("brands")
        if brands:
            all_brands = load_makes_from_csv()
            mmvm_parts = [f"{all_brands.get(b.lower())}|||" for b in brands]
            params["mmmv"] = ",".join(mmvm_parts)

        return f"{self.config.base_url}/search?" + urlencode(params)

    def extract_car_data(self, soup):
        """Extract relevant car data from the parsed HTML."""
        car_list = []
        listings = soup.find_all("article", class_="cldt-summary-full-item")

        if not listings:
            logger.warning("No car listings found on this page.")
            return car_list

        for car in listings:
            try:
                url = car.find("a", class_="ListItem_title__ndA4s")[
                    "href"
                ]  # Extract the URL

                full_url = f"https://www.autoscout24.com{url}"
                car_make = car.get("data-make", "").strip()
                car_model = car.get("data-model", "").strip()
                car_price = (
                    int(
                        car.get("data-price", "")
                        .replace("€", "")
                        .replace(".", "")
                        .strip()
                    )
                    if car.get("data-price")
                    else None
                )
                car_km = (
                    int(
                        car.get("data-mileage", "")
                        .replace("km", "")
                        .replace(",", "")
                        .strip()
                    )
                    if car.get("data-mileage")
                    else None
                )
                car_year = (
                    int(car.get("data-first-registration", "").split("-")[1])
                    if car.get("data-first-registration")
                    else None
                )

                if car_make in EXCLUDED_CARS:
                    if car_model in EXCLUDED_CARS[car_make]:
                        logger.debug("skipped %s | %s", car_make, car_model)
                        continue

                # Create a dictionary for the car data
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
                    car_list.append(car_data)
                    logger.debug(
                        "Scraped new car: %s | %s | %s euro | %skm",
                        car_make,
                        car_model,
                        car_price,
                        car_km,
                    )

            except (AttributeError, ValueError, IndexError, ScraperException) as e:
                logger.error(f"Error extracting data for a car: {e}")

        return car_list

    def scrape_car_details(self, url):
        """Scrape additional details from the car's individual listing page."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Initialize variables
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

            # Initialize additional details dictionary
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

            # Function to extract details from a section
            def extract_details(section_id):
                section = soup.find("section", id=section_id)
                if section:
                    for detail in section.find_all(
                        "dl", class_="DataGrid_defaultDlStyle__xlLi_"
                    ):
                        for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                            key = dt.text.strip()
                            if key in details_mapping:
                                if key in ["Seats", "Doors", "Previous owner"]:
                                    additional_details[details_mapping[key]] = int(
                                        dd.text.strip()
                                    )
                                elif key == "Mileage":
                                    additional_details["vehicle_mileage"] = int(
                                        dd.text.strip()
                                        .replace(" km", "")
                                        .replace(",", "")
                                        .strip()
                                    )
                                else:
                                    additional_details[details_mapping[key]] = (
                                        dd.text.strip()
                                    )

            # Extract details from all relevant sections
            extract_details("basic-details-section")
            extract_details("listing-history-section")
            extract_details("technical-details-section")
            extract_details("environment-details-section")

            # Extract equipment details
            equipment_section = soup.find("section", id="equipment-section")
            if equipment_section:
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

            return additional_details

        except requests.exceptions.RequestException as e:
            raise ScraperException(f"Error fetching details from {url}: {e}") from e
