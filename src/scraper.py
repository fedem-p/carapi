"""Scraper module for fetching car data from Autoscout24."""

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
    "volkswagen": ["caddy"],
    "opel": ["astra", "corsa", "grandland x", "grandland", "crossland x", "crossland"],
    "ford": ["puma"],
    "skoda": ["scala"],
    "hyundai": ["kona", "i20"],
    "toyota": ["c-hr"],
    "bmw": ["118"],
    "peugeot": ["208"],
    "nissan": ["micra"],
    "renault": ["zoe"],
    "citroen": ["c3"],
    "kia": ["rio"],
    "dacia": ["logan"],
    "seat": ["ibiza"]

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

    def scrape_data(self, sort_method= "standard"):
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

                # Extract the image URL (480p JPEG)
                image_tag = car.find("img", class_="NewGallery_img__cXZQC")
                image_url = image_tag["src"] if image_tag else None

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
                            "image_url": image_url,
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

            except (AttributeError, ValueError, IndexError) as e:
                logger.error(f"Error extracting data for a car: {e}")

        return car_list

    def scrape_car_details(self, url):
        """Scrape additional details from the car's individual listing page."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract additional details from the Basic Data section
            basic_data_section = soup.find("section", id="basic-details-section")
            if basic_data_section:
                details = basic_data_section.find_all(
                    "dl", class_="DataGrid_defaultDlStyle__xlLi_"
                )
                if details:
                    for detail in details:
                        for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                            if dt.text.strip() == "Body type":
                                body_type = dd.text.strip()
                            elif dt.text.strip() == "Type":
                                car_type = dd.text.strip()
                            elif dt.text.strip() == "Seats":
                                seats = int(dd.text.strip())
                            elif dt.text.strip() == "Doors":
                                doors = int(dd.text.strip())
                            elif dt.text.strip() == "Country version":
                                country_version = dd.text.strip()
                            elif dt.text.strip() == "Offer number":
                                offer_number = dd.text.strip()
                            elif dt.text.strip() == "Warranty":
                                warranty = dd.text.strip()

            # Extract additional details from the Vehicle History section
            history_section = soup.find("section", id="listing-history-section")
            if history_section:
                history_details = history_section.find_all(
                    "dl", class_="DataGrid_defaultDlStyle__xlLi_"
                )
                if history_details:
                    for detail in history_details:
                        for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                            if dt.text.strip() == "Mileage":
                                vehicle_mileage = int(
                                    dd.text.strip()
                                    .replace(" km", "")
                                    .replace(",", "")
                                    .strip()
                                )
                            elif dt.text.strip() == "First registration":
                                first_registration = dd.text.strip()
                            elif dt.text.strip() == "General inspection":
                                general_inspection = dd.text.strip()
                            elif dt.text.strip() == "Previous owner":
                                previous_owner = int(dd.text.strip())
                            elif dt.text.strip() == "Full service history":
                                full_service_history = dd.text.strip()
                            elif dt.text.strip() == "Non-smoker vehicle":
                                non_smoker_vehicle = dd.text.strip()

            # Extract additional details from the Technical Data section
            technical_section = soup.find("section", id="technical-details-section")
            if technical_section:
                technical_details = technical_section.find_all(
                    "dl", class_="DataGrid_defaultDlStyle__xlLi_"
                )
                if technical_details:
                    for detail in technical_details:
                        for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                            if dt.text.strip() == "Power":
                                power = dd.text.strip()
                            elif dt.text.strip() == "Gearbox":
                                gearbox = dd.text.strip()
                            elif dt.text.strip() == "Engine size":
                                engine_size = dd.text.strip()

            # Extract additional details from the Environmental Data section
            environment_section = soup.find("section", id="environment-details-section")
            if environment_section:
                environment_details = environment_section.find_all(
                    "dl", class_="DataGrid_defaultDlStyle__xlLi_"
                )
                if environment_details:
                    for detail in environment_details:
                        for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                            if dt.text.strip() == "Emission class":
                                emission_class = dd.text.strip()
                            elif dt.text.strip() == "Emissions sticker":
                                emissions_sticker = dd.text.strip()
                            elif dt.text.strip() == "Fuel type":
                                fuel_type = dd.text.strip()

            # Extract additional details from the Equipment section
            equipment_section = soup.find("section", id="equipment-section")
            if equipment_section:
                equipment_details = equipment_section.find_all(
                    "dl", class_="DataGrid_defaultDlStyle__xlLi_"
                )
                if equipment_details:
                    for detail in equipment_details:
                        for dt, dd in zip(detail.find_all("dt"), detail.find_all("dd")):
                            if dt.text.strip() == "Comfort & Convenience":
                                equipment_items = dd.find_all("li")
                                for item in equipment_items:
                                    if "Android Auto" in item.text:
                                        android_auto = True
                                    if "Apple CarPlay" in item.text:
                                        car_play = True
                                    if "Seat heating" in item.text:
                                        seat_heating = True
                            elif dt.text.strip() == "Safety & Security":
                                equipment_items = dd.find_all("li")
                                for item in equipment_items:
                                    if "Cruise Control" in item.text:
                                        cruise_control = True
                                    if "Adaptive Cruise Control" in item.text:
                                        adaptive_cruise_control = True

            # Create a dictionary for the additional car details
            additional_details = {
                "body_type": body_type if "body_type" in locals() else None,
                "car_type": car_type if "car_type" in locals() else None,
                "seats": seats if "seats" in locals() else None,
                "doors": doors if "doors" in locals() else None,
                "country_version": (
                    country_version if "country_version" in locals() else None
                ),
                "offer_number": offer_number if "offer_number" in locals() else None,
                "warranty": warranty if "warranty" in locals() else None,
                "vehicle_mileage": (
                    vehicle_mileage if "vehicle_mileage" in locals() else None
                ),
                "first_registration": (
                    first_registration if "first_registration" in locals() else None
                ),
                "general_inspection": (
                    general_inspection if "general_inspection" in locals() else None
                ),
                "previous_owner": (
                    previous_owner if "previous_owner" in locals() else None
                ),
                "full_service_history": (
                    full_service_history if "full_service_history" in locals() else None
                ),
                "non_smoker_vehicle": (
                    non_smoker_vehicle if "non_smoker_vehicle" in locals() else None
                ),
                "power": power if "power" in locals() else None,
                "engine_size": engine_size if "engine_size" in locals() else None,
                "emission_class": (
                    emission_class if "emission_class" in locals() else None
                ),
                "emission_sticker": (
                    emissions_sticker if "emissions_sticker" in locals() else None
                ),
                "fuel": fuel_type if "fuel_type" in locals() else None,
                "transmission": gearbox if "gearbox" in locals() else None,
                "android_auto": android_auto if "android_auto" in locals() else False,
                "car_play": car_play if "car_play" in locals() else False,
                "cruise_control": (
                    cruise_control if "cruise_control" in locals() else False
                ),
                "adaptive_cruise_control": (
                    adaptive_cruise_control
                    if "adaptive_cruise_control" in locals()
                    else False
                ),
                "seat_heating": seat_heating if "seat_heating" in locals() else False,
            }

            return additional_details

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching details from {url}: {e}")
            return None
