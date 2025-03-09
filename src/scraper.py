"""Scraper module for fetching car data from Autoscout24."""

import time
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup


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

    def scrape_data(self):
        """Scrape car data from the configured URL for the specified number of pages.

        Raises:
            ScraperException: If the request to the website fails or returns an error status.

        Returns:
            list: A list of dictionaries containing car data.
        """
        all_cars = []
        for page in range(
            1, self.config.num_pages + 1
        ):  # Loop through the specified number of pages
            url = self.construct_url(page)

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # This will raise an error for bad responses
            except requests.exceptions.Timeout as e:
                raise ScraperException(f"Request to {url} timed out: {e}")
            except requests.exceptions.RequestException as e:
                raise ScraperException(f"An error occurred: {e}")

            if response.status_code == 200:
                # Parse the response using BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                cars = self.extract_car_data(soup)
                all_cars.extend(cars)  # Add the cars from this page to the overall list
            else:
                raise ScraperException(
                    f"Failed to fetch data from page {page}: Status code {response.status_code}"
                )

            time.sleep(1)

        return all_cars

    def construct_url(self, page):
        """Construct the search URL with query parameters based on the filters.

        Args:
            page (int): The page number to fetch.

        Returns:
            str: The constructed URL for scraping car data.
        """
        # Build the URL with query parameters based on filters
        params = {
            "make": self.config.filters["make"],
            "model": self.config.filters["model"],
            "min_price": self.config.filters["min_price"],
            "max_price": self.config.filters["max_price"],
            "min_year": self.config.filters["min_year"],
            "max_year": self.config.filters["max_year"],
            "country": self.config.filters["country"],  # Added country filter
            "brands": ",".join(self.config.filters["brands"]),  # Added brands filter
            "page": page,  # Add the page number to the parameters
            # Add more parameters as needed
        }
        return f"{self.config.base_url}/search?" + urlencode(params)

    def extract_car_data(self, soup):
        """Extract relevant car data from the parsed HTML."""
        car_list = []
        for car in soup.find_all("div", class_="car-listing"):
            try:
                car_data = {
                    "make": car.find("span", class_="make").text.strip(),
                    "model": car.find("span", class_="model").text.strip(),
                    "price": int(
                        car.find("span", class_="price")
                        .text.replace("€", "")
                        .replace(",", "")
                        .strip()
                    ),
                    "year": int(car.find("span", class_="year").text.strip()),
                    # Add more fields as needed
                }
                car_list.append(car_data)
            except (AttributeError, ValueError) as e:
                # Log the error or handle it as needed
                print(f"Error extracting data for a car: {e}")
        return car_list
