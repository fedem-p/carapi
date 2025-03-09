"""Scraper docstring."""

from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup


class Scraper:
    """Scraper class"""

    def __init__(self, config):
        """_summary_

        Args:
            config (_type_): _description_
        """
        self.config = config

    def scrape_data(self):
        """_summary_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        # Construct the URL with filters
        url = self.construct_url()
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Parse the response using BeautifulSoup or similar
            soup = BeautifulSoup(response.text, "html.parser")
            cars = self.extract_car_data(soup)
            return cars

        raise Exception("Failed to fetch data from the website")

    def construct_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Build the URL with query parameters based on filters
        params = {
            "make": self.config.filters["make"],
            "model": self.config.filters["model"],
            "min_price": self.config.filters["min_price"],
            "max_price": self.config.filters["max_price"],
            "min_year": self.config.filters["min_year"],
            "max_year": self.config.filters["max_year"],
            # Add more parameters as needed
        }
        return f"{self.config.base_url}/search?" + urlencode(params)

    def extract_car_data(self, soup):
        """_summary_

        Args:
            soup (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Extract relevant car data from the parsed HTML
        car_list = []
        for car in soup.find_all("div", class_="car-listing"):
            car_data = {
                "make": car.find("span", class_="make").text,
                "model": car.find("span", class_="model").text,
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
        return car_list
