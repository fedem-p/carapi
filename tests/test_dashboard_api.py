import json
import pytest
from unittest.mock import patch
from dashboard.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_config(client):
    resp = client.get("/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "filters" in data
    assert "num_pages" in data
    assert "scoring_profiles" in data
    assert "excluded_cars" in data
    # Check label mapping
    assert isinstance(data["filters"].get("body", []), list)


def test_post_config(client):
    new_config = {
        "filters": {
            "body": ["Compact"],
            "fuel": ["Gasoline"],
            "sort": "price",
            "min_power": "100",
        },
        "num_pages": 3,
        "scoring_profiles": {"standard": {"weights": {"price": 2}}},
        "excluded_cars": {"ford": ["focus"]},
    }
    resp = client.post(
        "/config", data=json.dumps(new_config), content_type="application/json"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    # Confirm GET reflects changes
    resp2 = client.get("/config")
    data2 = resp2.get_json()
    assert data2["num_pages"] == 3
    assert "Compact" in data2["filters"]["body"]
    assert "Gasoline" in data2["filters"]["fuel"]
    assert data2["filters"]["sort"] == "price"


def test_post_config_invalid_json(client):
    resp = client.post("/config", data="not a json", content_type="application/json")
    assert resp.status_code == 400 or resp.get_json().get("status") == "error"


def test_notify_no_results(client):
    # Patch dashboard_state to have no results
    with patch("dashboard.app.dashboard_state", {"results": None}):
        resp = client.post("/notify")
        data = resp.get_json()
        assert data["status"] == "error"
        assert "No results" in data["error"]


def test_notify_success(client):
    # Patch dashboard_state and Notifier (patch Notifier in src.notifier)
    with patch("dashboard.app.dashboard_state", {"results": [{"car": "test"}]}):
        with patch("src.notifier.Notifier") as MockNotifier:
            instance = MockNotifier.return_value
            instance.send_email.return_value = None
            resp = client.post("/notify")
            data = resp.get_json()
            assert data["status"] == "success"
            instance.send_email.assert_called()
