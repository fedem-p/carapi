import pytest
from src.scraper import Scraper
import src.scraper as scraper_module
from unittest.mock import patch
import requests
from bs4 import BeautifulSoup

EXCLUDED_CARS = {
    "BrandA": ["ModelX", "ModelY"],
    "skoda": ["fabia"],
    "ssangyong": ["korando", "tivoli"],
}


class DummyConfig:
    def __init__(self):
        self.filters = {}
        self.base_url = "http://example.com"
        self.num_pages = 1
        self.excluded_cars = EXCLUDED_CARS


def test_filter_car_excludes():
    scraper = Scraper(DummyConfig())
    assert scraper._filter_car("BrandA", "ModelX") is True
    assert scraper._filter_car("BrandA", "OtherModel") is False
    assert scraper._filter_car("OtherBrand", "ModelX") is False


def test_clean_car_data_normalizes():
    scraper = Scraper(DummyConfig())
    dirty = {"price": "12.345€", "mileage": "123,456km", "year": "2020"}
    clean = scraper._clean_car_data(dirty.copy())
    assert clean["price"] == 12345
    assert clean["mileage"] == 123456
    assert clean["year"] == 2020

    # Test with missing/invalid values
    dirty = {"price": None, "mileage": "notanumber", "year": "notanumber"}
    clean = scraper._clean_car_data(dirty.copy())
    assert clean["price"] is None
    assert clean["mileage"] is None
    assert clean["year"] is None


def test_parse_price():
    scraper = Scraper(DummyConfig())
    assert scraper._parse_price("12.345€") == 12345
    assert scraper._parse_price(None) is None
    assert scraper._parse_price("") is None


def test_parse_km():
    scraper = Scraper(DummyConfig())
    assert scraper._parse_km("123,456km") == 123456
    assert scraper._parse_km(None) is None
    assert scraper._parse_km("") is None


def test_parse_year():
    scraper = Scraper(DummyConfig())
    assert scraper._parse_year("01-2020") == 2020
    assert scraper._parse_year(None) is None
    assert scraper._parse_year("") is None


def test_construct_url():
    config = DummyConfig()
    config.filters = {"body": [1, 2], "brands": ["testbrand"]}
    config.base_url = "http://example.com"
    scraper = Scraper(config)
    with patch("src.scraper.load_makes_from_csv", return_value={"testbrand": "123"}):
        url = scraper._construct_url(1, "standard")
        assert url.startswith("http://example.com/search?")
        assert "body=1%2C2" in url
        assert "mmmv=123%7C%7C%7C" in url


def test_parse_cars_from_html():
    scraper = Scraper(DummyConfig())
    with open("tests/autoscout_sample.html", encoding="utf-8") as f:
        html = f.read()
    with patch.object(
        scraper, "scrape_car_details", return_value={"test_detail": "value"}
    ):
        cars = scraper._parse_cars_from_html(html)
    assert isinstance(cars, list)
    # At least one car should be found in a real sample
    assert len(cars) == 17
    # Check that expected keys exist in the first car dict
    assert "make" in cars[0]
    assert "model" in cars[0]


def test_get_response_timeout(monkeypatch):
    scraper = Scraper(DummyConfig())

    def raise_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("timeout")

    monkeypatch.setattr(requests, "get", raise_timeout)
    assert scraper._get_response("http://fakeurl") is None


def test_get_response_request_exception(monkeypatch):
    scraper = Scraper(DummyConfig())

    def raise_request_exception(*args, **kwargs):
        raise requests.exceptions.RequestException("error")

    monkeypatch.setattr(requests, "get", raise_request_exception)
    assert scraper._get_response("http://fakeurl") is None


def test_extract_car_data_no_listings():
    scraper = Scraper(DummyConfig())
    html = "<html><body></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    cars = scraper.extract_car_data(soup)
    assert cars == []


def test_scrape_car_details_exception(monkeypatch):
    scraper = Scraper(DummyConfig())

    def raise_request_exception(*args, **kwargs):
        raise requests.exceptions.RequestException("error")

    monkeypatch.setattr(requests, "get", raise_request_exception)
    with pytest.raises(scraper_module.ScraperException):
        scraper.scrape_car_details("http://fakeurl")


def test_scrape_car_details_from_sample(monkeypatch):
    scraper = Scraper(DummyConfig())
    with open("tests/autoscout_sample_single_car.html", encoding="utf-8") as f:
        html = f.read()

    class MockResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse(html)

    monkeypatch.setattr(requests, "get", mock_get)
    details = scraper.scrape_car_details("http://fakeurl")
    assert isinstance(details, dict)
    # Assert exact values for several fields
    assert details["body_type"] == "Sedan"
    assert details["car_type"] == "Used"
    assert details["seats"] == 5
    assert details["doors"] == 4
    assert details["country_version"] == "Germany"
    assert details["offer_number"] == "1384-146"
    assert details["warranty"] is None
    assert details["vehicle_mileage"] == 255654
    assert details["first_registration"] == "08/2004"
    assert details["general_inspection"] == "New"
    assert details["previous_owner"] is None
    assert details["full_service_history"] == "Yes"
    assert details["non_smoker_vehicle"] is None
    assert details["power"] == "85 kW (116 hp)"
    assert details["gearbox"] == "Automatic"
    assert details["engine_size"] == "1,984 cc"
    assert details["emission_class"] == "Euro 4"
    assert details["emission_sticker"] == "1 (No sticker)"
    assert details["fuel_type"] == "Gasoline"
    assert details["android_auto"] is False
    assert details["car_play"] is False
    assert details["cruise_control"] is False
    assert details["adaptive_cruise_control"] is False
    assert details["seat_heating"] is False
    assert (
        details["img_url"]
        == "https://prod.pictures.autoscout24.net/listing-images/ac39c2df-580c-4f54-bc31-345eb24f9489_b545e5ca-bbcc-4527-9924-a188541aca8e.jpg/360x270.jpg"
    )
    # make/model are not in details, only in main listing
    assert "make" not in details
    assert "model" not in details
