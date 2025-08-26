"""Tests for the fetch_makes_and_models module."""

import os
import tempfile
import pytest
import requests
from unittest.mock import patch, mock_open, MagicMock
from src.fetch_makes_and_models import (
    fetch_makes_and_models,
    save_makes_to_csv,
    load_makes_from_csv,
    main
)


@pytest.fixture
def sample_api_response():
    """Sample API response data for testing."""
    return {
        "makes": [
            {
                "id": "1",
                "name": "BMW",
                "models": [
                    {"id": "101", "name": "3 Series"},
                    {"id": "102", "name": "X5"}
                ]
            },
            {
                "id": "2", 
                "name": "Audi",
                "models": [
                    {"id": "201", "name": "A4"},
                    {"id": "202", "name": "Q7"}
                ]
            },
            {
                "id": "3",
                "name": "Tesla",  # This might be filtered out depending on FILTER_MAKES
                "models": [
                    {"id": "301", "name": "Model S"}
                ]
            },
            {
                "id": "4",
                "name": "NoModelsBrand"  # Make without models key
            }
        ]
    }


@patch('requests.get')
def test_fetch_makes_and_models_success(mock_get, sample_api_response):
    """Test successful API fetch."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Call function
    result = fetch_makes_and_models()
    
    # Verify
    assert result == sample_api_response
    mock_get.assert_called_once_with(
        "https://listing-creation.api.autoscout24.com/makes?culture=de-DE&marketplace=de",
        headers={"accept": "application/json"},
        timeout=10
    )
    mock_response.raise_for_status.assert_called_once()


@patch('requests.get')
def test_fetch_makes_and_models_http_error(mock_get):
    """Test API fetch with HTTP error."""
    # Setup mock to raise HTTP error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_response
    
    # Call function and expect exception
    with pytest.raises(requests.HTTPError):
        fetch_makes_and_models()


@patch('requests.get')
def test_fetch_makes_and_models_timeout(mock_get):
    """Test API fetch with timeout."""
    # Setup mock to raise timeout
    mock_get.side_effect = requests.Timeout("Request timed out")
    
    # Call function and expect exception
    with pytest.raises(requests.Timeout):
        fetch_makes_and_models()


def test_save_makes_to_csv(sample_api_response):
    """Test saving makes to CSV with filtering."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Call function - this uses the actual FILTER_MAKES from constants
        save_makes_to_csv(sample_api_response, temp_filename)
        
        # Verify file was created
        assert os.path.exists(temp_filename)
        
        # Read and verify content
        with open(temp_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check header
        assert lines[0].strip() == "make_id,make_name,model_id,model_name"
        
        # Check content - based on actual FILTER_MAKES, BMW, Audi, and Tesla should all be included
        content = ''.join(lines)
        assert "BMW" in content
        assert "Audi" in content
        assert "Tesla" in content  # Tesla is in the actual FILTER_MAKES
        
        # NoModelsBrand should not be included as it's not in FILTER_MAKES
        assert "NoModelsBrand" not in content
        
        # Count lines (header + models)
        # BMW has 2 models, Audi has 2 models, Tesla has 1 model = 5 data lines + 1 header = 6 total
        assert len(lines) == 6
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


@patch('src.constants.FILTER_MAKES', ['BMW'])
def test_save_makes_to_csv_no_models_key(sample_api_response):
    """Test saving makes with no models key."""
    # Add a make without models key to test data
    test_data = {
        "makes": [
            {
                "id": "1",
                "name": "BMW",
                "models": [{"id": "101", "name": "3 Series"}]
            },
            {
                "id": "4", 
                "name": "BMW"  # This one has no models key
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Call function
        save_makes_to_csv(test_data, temp_filename)
        
        # Verify file was created
        assert os.path.exists(temp_filename)
        
        # Read and verify content
        with open(temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have both entries
        assert "BMW,101,3 Series" in content
        assert "BMW,," in content  # Empty model fields
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_load_makes_from_csv():
    """Test loading makes from CSV file."""
    # Create test CSV content
    csv_content = """make_id,make_name,model_id,model_name
1,BMW,101,3 Series
1,BMW,102,X5
2,Audi,201,A4
2,Audi,202,Q7
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(csv_content)
        temp_filename = tmp_file.name
    
    try:
        # Call function
        makes_mapping = load_makes_from_csv(temp_filename)
        
        # Verify results
        assert makes_mapping == {
            'bmw': '1',  # Lowercase key
            'audi': '2'
        }
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_load_makes_from_csv_empty_make_name():
    """Test loading makes from CSV with empty make names."""
    csv_content = """make_id,make_name,model_id,model_name
1,BMW,101,3 Series
2,,201,A4
3,Audi,202,Q7
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(csv_content)
        temp_filename = tmp_file.name
    
    try:
        # Call function
        makes_mapping = load_makes_from_csv(temp_filename)
        
        # Verify results - empty make name should be skipped
        assert makes_mapping == {
            'bmw': '1',
            'audi': '3'
        }
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_load_makes_from_csv_nonexistent_file():
    """Test loading from non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_makes_from_csv('nonexistent_file.csv')


@patch('src.fetch_makes_and_models.save_makes_to_csv')
@patch('src.fetch_makes_and_models.fetch_makes_and_models')
@patch('builtins.print')
def test_main_function(mock_print, mock_fetch, mock_save, sample_api_response):
    """Test main function."""
    # Setup mocks
    mock_fetch.return_value = sample_api_response
    
    # Call function
    main()
    
    # Verify calls
    mock_fetch.assert_called_once()
    mock_save.assert_called_once_with(sample_api_response)
    mock_print.assert_called_once()
    assert "Successfully saved makes and models" in mock_print.call_args[0][0]


def test_save_makes_to_csv_with_filter_exclusion(sample_api_response):
    """Test saving makes to CSV with some makes excluded by filter."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Call function - NoModelsBrand should be filtered out
        save_makes_to_csv(sample_api_response, temp_filename)
        
        # Verify file was created
        assert os.path.exists(temp_filename)
        
        # Read and verify content
        with open(temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should include makes that are in FILTER_MAKES
        assert "BMW" in content
        assert "Audi" in content
        assert "Tesla" in content
        
        # Should not include makes that are not in FILTER_MAKES
        assert "NoModelsBrand" not in content
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_save_makes_to_csv_case_sensitivity():
    """Test that make filtering respects exact case matching."""
    test_data = {
        "makes": [
            {"id": "1", "name": "bmw", "models": [{"id": "101", "name": "3 Series"}]},  # lowercase
            {"id": "2", "name": "BMW", "models": [{"id": "102", "name": "X5"}]},  # uppercase  
            {"id": "3", "name": "NotInFilter", "models": [{"id": "103", "name": "Test"}]}
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        save_makes_to_csv(test_data, temp_filename)
        
        # Read content
        with open(temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # BMW (uppercase) should be included since it's in FILTER_MAKES
        assert "BMW,102,X5" in content
        # lowercase bmw should not be included
        assert "bmw,101,3 Series" not in content
        # NotInFilter should not be included
        assert "NotInFilter" not in content
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)