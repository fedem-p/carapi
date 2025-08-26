import pytest
from unittest.mock import patch
import pandas as pd
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Now import AutoScore
from auto_score import AutoScore


# Fixture for mocking the car data
@pytest.fixture
def mock_data():
    """Fixture to mock sample car data."""
    return pd.DataFrame(
        {
            "url": ["url1", "url2", "url3"],
            "price": [10000, 15000, 20000],
            "mileage": [50000, 60000, 70000],
            "fuel_type": ["petrol", "diesel", "electric"],
            "android_auto": [True, True, False],
            "car_play": [True, True, True],
            "adaptive_cruise_control": [True, False, False],
            "seat_heating": [True, True, False],
            "power": ["150 hp", "180 hp", "200 hp"],
            "year": [2018, 2019, 2020],
            "body_type": ["sedan", "station wagon", "off-road/pick-up"],
            "emission_class": ["6", "5", "6"],
            "make": ["BMW", "Audi", "Mercedes"],
            "model": ["3 Series", "A4", "G-Class"],
            "warranty": ["yes", "no", "yes"],
            "previous_owner": [1, 2, 1],
            "full_service_history": ["yes", "no", "yes"],
            "non_smoker_vehicle": ["yes", "yes", "no"],
        }
    )


# Helper function to create an AutoScore instance with mock data
def create_autoscore(mock_listdir, mock_read_csv, mock_data):
    """Helper function to initialize AutoScore with mock data."""
    mock_listdir.return_value = ["file1.csv", "file2.csv"]
    mock_read_csv.return_value = mock_data
    return AutoScore(folder_path="mock_folder")


# Patch decorators combined to reduce redundancy
@patch("pandas.read_csv")
@patch("os.listdir")
def test_autoscore_initialization(mock_listdir, mock_read_csv, mock_data):
    """Test initialization of AutoScore class."""
    autoscore = create_autoscore(mock_listdir, mock_read_csv, mock_data)

    assert autoscore.data.shape[0] == 3, "Data should contain 3 rows"
    assert "url" in autoscore.data.columns, "'url' column should exist"
    assert (
        "score" not in autoscore.data.columns
    ), "'score' column should not exist initially"


@patch("pandas.read_csv")
@patch("os.listdir")
def test_normalize(mock_listdir, mock_read_csv, mock_data):
    """Test the normalization function."""
    autoscore = create_autoscore(mock_listdir, mock_read_csv, mock_data)

    # Normalize a value (should be 0.5 based on the example in the original code)
    normalized_value = autoscore.normalize(10, 0, 20)
    assert normalized_value == 0.5, "Normalized value should be 0.5"


@patch("pandas.read_csv")
@patch("os.listdir")
def test_score_car(mock_listdir, mock_read_csv, mock_data):
    """Test the scoring function for a single car."""
    autoscore = create_autoscore(mock_listdir, mock_read_csv, mock_data)

    # Test scoring for the first car in mock data
    car = mock_data.iloc[0]
    score = autoscore.score_car(car)

    assert isinstance(score, float), "Score should be a float"


@patch("pandas.read_csv")
@patch("os.listdir")
def test_assign_grade(mock_listdir, mock_read_csv, mock_data):
    """Test the grade assignment function."""
    autoscore = create_autoscore(mock_listdir, mock_read_csv, mock_data)

    # Test for different score ranges
    assert autoscore.assign_grade(29) == "Outstanding"
    assert autoscore.assign_grade(26) == "Excellent"
    assert autoscore.assign_grade(22) == "Good"
    assert autoscore.assign_grade(18) == "Decent"
    assert autoscore.assign_grade(13) == "Not Good"
    assert autoscore.assign_grade(8) == "Bad"


@patch("pandas.read_csv")
@patch("os.listdir")
def test_rank_cars(mock_listdir, mock_read_csv, mock_data):
    """Test the ranking function."""
    autoscore = create_autoscore(mock_listdir, mock_read_csv, mock_data)

    ranked_cars = autoscore.rank_cars(n=2, save=False)  # Get top 2 cars

    assert ranked_cars.shape[0] == 2, "There should be 2 ranked cars"
    assert (
        ranked_cars["score"].iloc[0] >= ranked_cars["score"].iloc[1]
    ), "Cars should be ranked by score in descending order"


@patch("pandas.read_csv")
@patch("os.listdir")
def test_rank_unique_cars(mock_listdir, mock_read_csv, mock_data):
    """Test ranking when there are duplicates in car make-model."""
    autoscore = create_autoscore(mock_listdir, mock_read_csv, mock_data)

    # Create duplicate data by concatenating mock_data to itself
    duplicate_data = pd.concat([mock_data, mock_data], ignore_index=True)
    autoscore.data = duplicate_data

    ranked_cars = autoscore.rank_cars(n=3, save=False)  # Get top 3 cars

    # Ensure that only unique cars by make and model are considered
    assert (
        len(ranked_cars.drop_duplicates(subset=["make", "model"])) == 3
    ), "There should be 3 unique cars based on make-model"


@patch("pandas.read_csv")
@patch("os.listdir")
def test_normalize_with_empty_data(mock_listdir, mock_read_csv, mock_data):
    """Test normalization with empty data (edge case)."""
    autoscore = create_autoscore(mock_listdir, mock_read_csv, mock_data)
    autoscore.data = pd.DataFrame(columns=["price", "mileage"])  # Empty data

    # Test normalization on empty data
    normalized_value = autoscore.normalize(10, 0, 0)
    assert (
        normalized_value == 1
    ), "Normalization should return 1 when min == max (edge case)"
