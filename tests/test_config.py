import os
import tempfile
import json
import pytest
from src.config import Config, load_settings, save_settings

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "../settings.json")


@pytest.fixture(autouse=True)
def temp_settings_file(monkeypatch):
    # Backup and restore the settings file
    orig_path = SETTINGS_PATH
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    monkeypatch.setattr("src.config.SETTINGS_PATH", temp_path)
    # Write a default config
    default = {
        "filters": {
            "body": ["1"],
            "fuel": ["B"],
            "sort": "standard",
            "min_power": "74",
        },
        "num_pages": 2,
        "scoring_profiles": {"standard": {"weights": {"price": 1}}},
        "excluded_cars": {"ford": ["fiesta"]},
    }
    with open(temp_path, "w") as f:
        json.dump(default, f)
    yield
    os.remove(temp_path)


def test_load_and_save_settings():
    settings = load_settings()
    assert "filters" in settings
    settings["filters"]["body"] = ["2"]
    save_settings(settings)
    loaded = load_settings()
    assert loaded["filters"]["body"] == ["2"]


def test_config_init_and_save():
    config = Config()
    assert config.filters["body"] == ["1"]
    config.filters["body"] = ["3"]
    config.save()
    loaded = load_settings()
    assert loaded["filters"]["body"] == ["3"]


def test_get_filters_for_frontend_label_mapping():
    config = Config()
    config.filters = {
        "body": ["1", "2"],
        "fuel": ["B", "D"],
        "sort": "price",
        "min_power": "100",
    }
    frontend = config.get_filters_for_frontend()
    assert frontend["body"] == ["Compact", "Convertible"]
    assert frontend["fuel"] == ["Gasoline", "Diesel"]
    assert frontend["sort"] == "price"
    assert isinstance(frontend["min_power"], str)


def test_set_filters_from_frontend_label_mapping():
    config = Config()
    frontend = {
        "body": ["Compact", "Convertible"],
        "fuel": ["Gasoline", "Diesel"],
        "sort": "age",
        "min_power": "134",
    }
    backend = config.set_filters_from_frontend(frontend)
    assert backend["body"] == ["1", "2"]
    assert backend["fuel"] == ["B", "D"]
    assert backend["sort"] == "age"
    assert isinstance(backend["min_power"], str)


def test_min_power_conversion():
    config = Config()
    # kW to HP for frontend
    config.filters = {"min_power": "100"}
    frontend = config.get_filters_for_frontend()
    assert frontend["min_power"] == str(round(100 * 1.341022))
    # HP to kW for backend
    frontend = {"min_power": "134"}
    backend = config.set_filters_from_frontend(frontend)
    assert backend["min_power"] == str(round(134 / 1.341022))
