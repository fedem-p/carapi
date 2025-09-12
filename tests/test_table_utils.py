"""Tests for the table_utils module."""

import pandas as pd
import pytest
from src.table_utils import get_table_html


@pytest.fixture
def sample_cars_df():
    """Sample car DataFrame for testing."""
    return pd.DataFrame(
        [
            {
                "make": "BMW",
                "model": "3 Series",
                "price": 25000,
                "mileage": 50000,
                "year": 2020,
                "score": 22.5,
                "grade": "Good",
                "url": "https://example.com/bmw",
                "img_url": "https://example.com/bmw.jpg",
            },
            {
                "make": "Audi",
                "model": "A4",
                "price": 30000,
                "mileage": 40000,
                "year": 2021,
                "score": 26.0,
                "grade": "Excellent",
                "url": "https://example.com/audi",
                "img_url": "https://example.com/audi.jpg",
            },
        ]
    )


def test_get_table_html_basic_structure(sample_cars_df):
    """Test that get_table_html returns valid HTML structure."""
    html = get_table_html(sample_cars_df)

    # Check basic HTML structure
    assert "<html>" in html
    assert "</html>" in html
    assert "<body>" in html
    assert "</body>" in html
    assert "<table" in html
    assert "</table>" in html
    assert "<h2>Latest Car Listings</h2>" in html


def test_get_table_html_headers(sample_cars_df):
    """Test that HTML table contains correct headers."""
    html = get_table_html(sample_cars_df)

    # Check table headers
    assert "<th>Make</th>" in html
    assert "<th>Model</th>" in html
    assert "<th>Price</th>" in html
    assert "<th>Mileage</th>" in html
    assert "<th>Year</th>" in html
    assert "<th>Score</th>" in html
    assert "<th>Grade</th>" in html
    assert "<th>Listing</th>" in html
    assert "<th>Image</th>" in html


def test_get_table_html_data_content(sample_cars_df):
    """Test that HTML table contains correct data."""
    html = get_table_html(sample_cars_df)

    # Check car data is present
    assert "BMW" in html
    assert "3 Series" in html
    assert "25000" in html
    assert "50000" in html
    assert "2020" in html
    assert "22.5" in html
    assert "Good" in html

    assert "Audi" in html
    assert "A4" in html
    assert "30000" in html
    assert "40000" in html
    assert "2021" in html
    assert "26.0" in html
    assert "Excellent" in html


def test_get_table_html_clickable_links(sample_cars_df):
    """Test that URLs are converted to clickable links."""
    html = get_table_html(sample_cars_df)

    # Check that URLs are converted to clickable links
    assert '<a href="https://example.com/bmw">Link</a>' in html
    assert '<a href="https://example.com/audi">Link</a>' in html


def test_get_table_html_images(sample_cars_df):
    """Test that images are included in the HTML."""
    html = get_table_html(sample_cars_df)

    # Check that images are included
    assert '<img src="https://example.com/bmw.jpg"' in html
    assert '<img src="https://example.com/audi.jpg"' in html
    assert 'class="table-img"' in html
    assert 'alt="car image"' in html


def test_get_table_html_score_highlighting(sample_cars_df):
    """Test that high scores are highlighted."""
    html = get_table_html(sample_cars_df)

    # Check for highlighting of high scores (> 24)
    # The Audi has score 26.0, so it should be highlighted
    assert "background-color: yellow;" in html

    # Count the number of highlighted rows (should be 1)
    highlighted_rows = html.count("background-color: yellow;")
    assert highlighted_rows == 1


def test_get_table_html_empty_dataframe():
    """Test get_table_html with empty DataFrame."""
    empty_df = pd.DataFrame(
        columns=[
            "make",
            "model",
            "price",
            "mileage",
            "year",
            "score",
            "grade",
            "url",
            "img_url",
        ]
    )

    html = get_table_html(empty_df)

    # Should still have basic structure
    assert "<html>" in html
    assert "<table" in html
    assert "<th>Make</th>" in html
    # But no data rows (only header row)
    assert "<td>" not in html


def test_get_table_html_table_structure():
    """Test that the HTML table has proper structure attributes."""
    sample_df = pd.DataFrame(
        [
            {
                "make": "Test",
                "model": "Car",
                "price": 10000,
                "mileage": 20000,
                "year": 2020,
                "score": 20.0,
                "grade": "Decent",
                "url": "https://test.com",
                "img_url": "https://test.com/img.jpg",
            }
        ]
    )

    html = get_table_html(sample_df)

    # Check table attributes
    assert 'border="1"' in html
    assert 'cellspacing="0"' in html
    assert 'cellpadding="5"' in html


def test_get_table_html_no_highlighting_low_score():
    """Test that low scores are not highlighted."""
    low_score_df = pd.DataFrame(
        [
            {
                "make": "Test",
                "model": "Car",
                "price": 10000,
                "mileage": 20000,
                "year": 2020,
                "score": 15.0,  # Low score, should not be highlighted
                "grade": "Not Good",
                "url": "https://test.com",
                "img_url": "https://test.com/img.jpg",
            }
        ]
    )

    html = get_table_html(low_score_df)

    # Should not contain highlighting for low scores
    assert "background-color: yellow;" not in html
    # But should still contain the data
    assert "Test" in html
    assert "15.0" in html
