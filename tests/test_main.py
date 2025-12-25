"""Tests for the main module."""

import pytest
from unittest.mock import patch, MagicMock
from src.main import main


@patch("src.main.Notifier")
@patch("src.main.AutoScore")
@patch("src.main.Exporter")
@patch("src.main.Scraper")
@patch("src.main.Config")
@patch("builtins.print")
def test_main_basic_flow(
    mock_print,
    mock_config_class,
    mock_scraper_class,
    mock_exporter_class,
    mock_autoscore_class,
    mock_notifier_class,
):
    """Test basic main function flow without email."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config_class.return_value = mock_config

    mock_scraper = MagicMock()
    mock_scraper_class.return_value = mock_scraper
    sample_cars = [{"make": "BMW", "model": "3 Series", "price": 25000}]
    mock_scraper.scrape_data.return_value = sample_cars

    mock_exporter = MagicMock()
    mock_exporter_class.return_value = mock_exporter

    mock_autoscore = MagicMock()
    mock_autoscore_class.return_value = mock_autoscore
    import pandas as pd

    mock_ranked_cars = pd.DataFrame(
        [
            {
                "make": "BMW",
                "model": "3 Series",
                "price": 25000,
                "mileage": 50000,
                "year": 2020,
                "score": 22.5,
                "grade": "Good",
                "url": "https://example.com",
            }
        ]
    )
    mock_autoscore.rank_cars.return_value = mock_ranked_cars

    # Mock command line arguments to not send email
    with patch("sys.argv", ["main.py"]):
        with patch("os.environ.get", return_value="false"):
            main()

    # Verify calls
    mock_config_class.assert_called_once()
    mock_scraper_class.assert_called_once_with(mock_config)

    # Should scrape with 3 different sort methods
    assert mock_scraper.scrape_data.call_count == 3
    expected_sorts = ["standard", "price", "age"]
    actual_sorts = [
        call[1]["sort_method"] for call in mock_scraper.scrape_data.call_args_list
    ]
    assert actual_sorts == expected_sorts

    # Should create 3 exporters and export 3 files
    assert mock_exporter_class.call_count == 3
    assert mock_exporter.export_to_csv.call_count == 3

    # Should analyze data once
    mock_autoscore_class.assert_called_once_with("data/results")
    mock_autoscore.rank_cars.assert_called_once_with(n=20)

    # Should not create notifier since email is false
    mock_notifier_class.assert_not_called()


@patch("src.main.Notifier")
@patch("src.main.AutoScore")
@patch("src.main.Exporter")
@patch("src.main.Scraper")
@patch("src.main.Config")
@patch("builtins.print")
def test_main_with_email_flag(
    mock_print,
    mock_config_class,
    mock_scraper_class,
    mock_exporter_class,
    mock_autoscore_class,
    mock_notifier_class,
):
    """Test main function with email flag enabled."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.settings_path = "/expected/path"
    mock_config_class.return_value = mock_config

    mock_scraper = MagicMock()
    mock_scraper_class.return_value = mock_scraper
    sample_cars = [{"make": "BMW", "model": "3 Series", "price": 25000}]
    mock_scraper.scrape_data.return_value = sample_cars

    mock_exporter = MagicMock()
    mock_exporter_class.return_value = mock_exporter

    mock_autoscore = MagicMock()
    mock_autoscore_class.return_value = mock_autoscore
    import pandas as pd

    mock_ranked_cars = pd.DataFrame(
        [
            {
                "make": "BMW",
                "model": "3 Series",
                "price": 25000,
                "mileage": 50000,
                "year": 2020,
                "score": 22.5,
                "grade": "Good",
                "url": "https://example.com",
            }
        ]
    )
    mock_autoscore.rank_cars.return_value = mock_ranked_cars

    mock_notifier = MagicMock()
    mock_notifier_class.return_value = mock_notifier

    # Mock command line arguments with email flag
    with patch("sys.argv", ["main.py", "--email"]):
        with patch("os.environ.get", return_value="false"):
            main()

    # Verify email functionality
    mock_notifier_class.assert_called_once_with(mock_config)
    mock_notifier.send_email.assert_called_once_with(
        "Latest Car Listings: /expected/path", mock_ranked_cars
    )

    # Verify send email message is printed
    mock_print.assert_any_call("Send email notifications: True")


@patch("src.main.Notifier")
@patch("src.main.AutoScore")
@patch("src.main.Exporter")
@patch("src.main.Scraper")
@patch("src.main.Config")
@patch("builtins.print")
def test_main_with_email_env_var(
    mock_print,
    mock_config_class,
    mock_scraper_class,
    mock_exporter_class,
    mock_autoscore_class,
    mock_notifier_class,
):
    """Test main function with email environment variable enabled."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.settings_path = "/expected/path"
    mock_config_class.return_value = mock_config

    mock_scraper = MagicMock()
    mock_scraper_class.return_value = mock_scraper
    sample_cars = [{"make": "BMW", "model": "3 Series", "price": 25000}]
    mock_scraper.scrape_data.return_value = sample_cars

    mock_exporter = MagicMock()
    mock_exporter_class.return_value = mock_exporter

    mock_autoscore = MagicMock()
    mock_autoscore_class.return_value = mock_autoscore
    import pandas as pd

    mock_ranked_cars = pd.DataFrame(
        [
            {
                "make": "BMW",
                "model": "3 Series",
                "price": 25000,
                "mileage": 50000,
                "year": 2020,
                "score": 22.5,
                "grade": "Good",
                "url": "https://example.com",
            }
        ]
    )
    mock_autoscore.rank_cars.return_value = mock_ranked_cars

    mock_notifier = MagicMock()
    mock_notifier_class.return_value = mock_notifier

    # Mock command line arguments without email flag but with env var
    with patch("sys.argv", ["main.py"]):
        with patch("os.environ.get", return_value="true"):
            main()

    # Verify email functionality
    mock_notifier_class.assert_called_once_with(mock_config)
    mock_notifier.send_email.assert_called_once_with(
        "Latest Car Listings: /expected/path", mock_ranked_cars
    )

    # Verify send email message is printed
    mock_print.assert_any_call("Send email notifications: True")


@patch("src.main.Notifier")
@patch("src.main.AutoScore")
@patch("src.main.Exporter")
@patch("src.main.Scraper")
@patch("src.main.Config")
@patch("builtins.print")
def test_main_export_filenames(
    mock_print,
    mock_config_class,
    mock_scraper_class,
    mock_exporter_class,
    mock_autoscore_class,
    mock_notifier_class,
):
    """Test that main exports to correct filenames."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config_class.return_value = mock_config

    mock_scraper = MagicMock()
    mock_scraper_class.return_value = mock_scraper
    sample_cars = [{"make": "BMW", "model": "3 Series", "price": 25000}]
    mock_scraper.scrape_data.return_value = sample_cars

    mock_exporter = MagicMock()
    mock_exporter_class.return_value = mock_exporter

    mock_autoscore = MagicMock()
    mock_autoscore_class.return_value = mock_autoscore
    import pandas as pd

    mock_ranked_cars = pd.DataFrame(
        [
            {
                "make": "BMW",
                "model": "3 Series",
                "price": 25000,
                "mileage": 50000,
                "year": 2020,
                "score": 22.5,
                "grade": "Good",
                "url": "https://example.com",
            }
        ]
    )
    mock_autoscore.rank_cars.return_value = mock_ranked_cars

    # Mock command line arguments
    with patch("sys.argv", ["main.py"]):
        with patch("os.environ.get", return_value="false"):
            main()

    # Verify export filenames
    expected_filenames = [
        "data/results/filtered_cars_standard.csv",
        "data/results/filtered_cars_price.csv",
        "data/results/filtered_cars_age.csv",
    ]
    actual_filenames = [
        call[0][0] for call in mock_exporter.export_to_csv.call_args_list
    ]
    assert actual_filenames == expected_filenames


@patch("src.main.AutoScore")
@patch("src.main.Exporter")
@patch("src.main.Scraper")
@patch("src.main.Config")
@patch("builtins.print")
def test_main_print_messages(
    mock_print,
    mock_config_class,
    mock_scraper_class,
    mock_exporter_class,
    mock_autoscore_class,
):
    """Test that main prints expected messages."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config_class.return_value = mock_config

    mock_scraper = MagicMock()
    mock_scraper_class.return_value = mock_scraper
    sample_cars = [{"make": "BMW", "model": "3 Series", "price": 25000}]
    mock_scraper.scrape_data.return_value = sample_cars

    mock_exporter = MagicMock()
    mock_exporter_class.return_value = mock_exporter

    mock_autoscore = MagicMock()
    mock_autoscore_class.return_value = mock_autoscore
    import pandas as pd

    mock_ranked_cars = pd.DataFrame(
        [
            {
                "make": "BMW",
                "model": "3 Series",
                "price": 25000,
                "mileage": 50000,
                "year": 2020,
                "score": 22.5,
                "grade": "Good",
                "url": "https://example.com",
            }
        ]
    )
    mock_autoscore.rank_cars.return_value = mock_ranked_cars

    # Mock command line arguments
    with patch("sys.argv", ["main.py"]):
        with patch("os.environ.get", return_value="false"):
            main()

    # Verify print messages
    mock_print.assert_any_call("Send email notifications: False")
    mock_print.assert_any_call(
        "================ Scraping with sorting: standard ================"
    )
    mock_print.assert_any_call(
        "================ Scraping with sorting: price ================"
    )
    mock_print.assert_any_call(
        "================ Scraping with sorting: age ================"
    )


def test_main_can_be_imported():
    """Test that main function can be imported without errors."""
    from src.main import main

    assert callable(main)
