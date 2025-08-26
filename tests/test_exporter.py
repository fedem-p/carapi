"""Tests for the exporter module."""

import os
import tempfile
import pytest
import pandas as pd
from src.exporter import Exporter


@pytest.fixture
def sample_cars():
    """Sample car data for testing."""
    return [
        {
            "make": "BMW",
            "model": "3 Series",
            "price": 25000,
            "mileage": 50000,
            "year": 2020,
            "fuel": "Gasoline",
            "url": "https://example.com/bmw"
        },
        {
            "make": "Audi",
            "model": "A4",
            "price": 30000,
            "mileage": 40000,
            "year": 2021,
            "fuel": "Diesel",
            "url": "https://example.com/audi"
        }
    ]


def test_exporter_initialization(sample_cars):
    """Test Exporter initialization."""
    exporter = Exporter(sample_cars)
    assert exporter.cars == sample_cars


def test_export_to_csv(sample_cars):
    """Test exporting car data to CSV file."""
    exporter = Exporter(sample_cars)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Export data
        exporter.export_to_csv(temp_filename)
        
        # Verify file was created
        assert os.path.exists(temp_filename)
        
        # Verify content
        df = pd.read_csv(temp_filename)
        assert len(df) == 2
        assert list(df['make']) == ['BMW', 'Audi']
        assert list(df['model']) == ['3 Series', 'A4']
        assert list(df['price']) == [25000, 30000]
        
    finally:
        # Clean up
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_import_from_csv(sample_cars):
    """Test importing car data from CSV file."""
    # First export data to create a CSV file
    exporter = Exporter(sample_cars)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Export data
        exporter.export_to_csv(temp_filename)
        
        # Import data back
        imported_cars = exporter.import_from_csv(temp_filename)
        
        # Verify imported data
        assert len(imported_cars) == 2
        assert imported_cars[0]['make'] == 'BMW'
        assert imported_cars[0]['model'] == '3 Series'
        assert imported_cars[0]['price'] == 25000
        assert imported_cars[1]['make'] == 'Audi'
        assert imported_cars[1]['model'] == 'A4'
        assert imported_cars[1]['price'] == 30000
        
    finally:
        # Clean up
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_export_empty_list():
    """Test exporting empty car list."""
    exporter = Exporter([])
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Export empty data
        exporter.export_to_csv(temp_filename)
        
        # Verify file was created
        assert os.path.exists(temp_filename)
        
        # For empty data, pandas creates an empty CSV
        # We need to handle the empty file case
        with open(temp_filename, 'r') as f:
            content = f.read().strip()
            # Empty DataFrame creates empty file
            assert content == ""
        
    finally:
        # Clean up
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_import_nonexistent_file():
    """Test importing from non-existent file raises error."""
    exporter = Exporter([])
    
    with pytest.raises(FileNotFoundError):
        exporter.import_from_csv('nonexistent_file.csv')


def test_round_trip_consistency(sample_cars):
    """Test that export followed by import preserves data integrity."""
    exporter = Exporter(sample_cars)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Export and import
        exporter.export_to_csv(temp_filename)
        imported_cars = exporter.import_from_csv(temp_filename)
        
        # Verify round-trip consistency
        assert len(imported_cars) == len(sample_cars)
        
        # Sort both lists by make for comparison
        original_sorted = sorted(sample_cars, key=lambda x: x['make'])
        imported_sorted = sorted(imported_cars, key=lambda x: x['make'])
        
        for orig, imported in zip(original_sorted, imported_sorted):
            assert orig['make'] == imported['make']
            assert orig['model'] == imported['model']
            assert orig['price'] == imported['price']
            assert orig['mileage'] == imported['mileage']
            assert orig['year'] == imported['year']
            assert orig['fuel'] == imported['fuel']
            assert orig['url'] == imported['url']
        
    finally:
        # Clean up
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)