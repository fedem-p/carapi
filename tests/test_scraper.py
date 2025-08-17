import pytest
from src.scraper import Scraper
import src.scraper as scraper_module
from unittest.mock import patch
import requests
from bs4 import BeautifulSoup

EXCLUDED_CARS = {"BrandA": ["ModelX", "ModelY"]}

class DummyConfig:
    def __init__(self):
        self.filters = {}
        self.base_url = "http://example.com"
        self.num_pages = 1


def test_filter_car_excludes():
    scraper = Scraper(DummyConfig())
    with patch.object(scraper_module, 'EXCLUDED_CARS', EXCLUDED_CARS):
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


def test_clean_car_data_comprehensive():
    """Test comprehensive data cleaning for all field types."""
    scraper = Scraper(DummyConfig())
    
    # Test with complex real-world data
    dirty = {
        "price": "25.000€",
        "mileage": "50,000km", 
        "year": "2018",
        "vehicle_mileage": "50000 km",
        "seats": "5",
        "doors": "4",
        "previous_owner": "2",
        "fuel_type": "Gasoline",
        "body_type": None,
        "emission_class": "",
        "make": "BMW",
        "model": None,
        "warranty": "Yes",
        "full_service_history": "No",
        "non_smoker_vehicle": None,
        "power": "150 hp",
        "android_auto": "true",
        "car_play": False,
        "cruise_control": "yes",
        "adaptive_cruise_control": None,
        "seat_heating": 1
    }
    
    clean = scraper._clean_car_data(dirty.copy())
    
    # Test numeric fields
    assert clean["price"] == 25000
    assert clean["mileage"] == 50000
    assert clean["year"] == 2018
    assert clean["vehicle_mileage"] == 50000
    assert clean["seats"] == 5
    assert clean["doors"] == 4
    assert clean["previous_owner"] == 2
    
    # Test string fields
    assert clean["fuel_type"] == "Gasoline"
    assert clean["body_type"] == ""  # None converted to empty string
    assert clean["emission_class"] == ""  # Empty string remains empty
    assert clean["make"] == "BMW"
    assert clean["model"] == ""  # None converted to empty string
    assert clean["warranty"] == "Yes"
    assert clean["full_service_history"] == "No"
    assert clean["non_smoker_vehicle"] == ""  # None converted to empty string
    assert clean["power"] == "150 hp"
    
    # Test boolean fields
    assert clean["android_auto"] is True  # "true" string converted to True
    assert clean["car_play"] is False
    assert clean["cruise_control"] is True  # "yes" string converted to True
    assert clean["adaptive_cruise_control"] is False  # None converted to False
    assert clean["seat_heating"] is True  # 1 converted to True


def test_clean_car_data_invalid_integers():
    """Test cleaning of invalid integer fields."""
    scraper = Scraper(DummyConfig())
    
    dirty = {
        "seats": "invalid",
        "doors": None,
        "previous_owner": "not_a_number",
        "vehicle_mileage": "abc km"
    }
    
    clean = scraper._clean_car_data(dirty.copy())
    
    assert clean["seats"] is None
    assert clean["doors"] is None
    assert clean["previous_owner"] is None
    assert clean["vehicle_mileage"] is None


def test_clean_car_data_boolean_variations():
    """Test various boolean input formats."""
    scraper = Scraper(DummyConfig())
    
    test_cases = [
        {"android_auto": "True", "expected": True},
        {"android_auto": "true", "expected": True},
        {"android_auto": "YES", "expected": True},
        {"android_auto": "yes", "expected": True},
        {"android_auto": "1", "expected": True},
        {"android_auto": "false", "expected": False},
        {"android_auto": "no", "expected": False},
        {"android_auto": "0", "expected": False},
        {"android_auto": "", "expected": False},
        {"android_auto": "random", "expected": False},
    ]
    
    for test_case in test_cases:
        clean = scraper._clean_car_data(test_case.copy())
        assert clean["android_auto"] == test_case["expected"], f"Failed for input: {test_case['android_auto']}"


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
    config.filters = {"body": [1,2], "brands": ["testbrand"]}
    config.base_url = "http://example.com"
    scraper = Scraper(config)
    with patch('src.scraper.load_makes_from_csv', return_value={"testbrand": "123"}):
        url = scraper._construct_url(1, "standard")
        assert url.startswith("http://example.com/search?")
        assert "body=1%2C2" in url
        assert "mmmv=123%7C%7C%7C" in url


def test_parse_cars_from_html():
    scraper = Scraper(DummyConfig())
    with open("tests/autoscout_sample.html", encoding="utf-8") as f:
        html = f.read()
    with patch.object(scraper, 'scrape_car_details', return_value={"test_detail": "value"}):
        cars = scraper._parse_cars_from_html(html)
    assert isinstance(cars, list)
    # At least one car should be found in a real sample
    assert len(cars) == 14
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
    assert details["img_url"] == "https://prod.pictures.autoscout24.net/listing-images/ac39c2df-580c-4f54-bc31-345eb24f9489_b545e5ca-bbcc-4527-9924-a188541aca8e.jpg/360x270.jpg"
    # make/model are not in details, only in main listing
    assert "make" not in details
    assert "model" not in details
