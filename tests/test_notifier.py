"""Tests for the notifier module."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import smtplib
from src.notifier import Notifier


class MockConfig:
    """Mock configuration for testing."""

    def __init__(self):
        self.email_settings = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "testpass",
            "recipient": "recipient@example.com",
        }


@pytest.fixture
def mock_config():
    """Mock configuration fixture."""
    return MockConfig()


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
            }
        ]
    )


@pytest.fixture
def sample_cars_list():
    """Sample car list for testing."""
    return [
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
        }
    ]


def test_notifier_initialization(mock_config):
    """Test Notifier initialization."""
    notifier = Notifier(mock_config)
    assert notifier.config == mock_config


@patch("src.notifier.get_table_html")
@patch("smtplib.SMTP")
def test_send_email_success_with_dataframe(
    mock_smtp, mock_get_table_html, mock_config, sample_cars_df
):
    """Test successful email sending with DataFrame input."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_df)

    # Verify SMTP was called correctly
    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("test@example.com", "testpass")
    mock_smtp_instance.sendmail.assert_called_once()

    # Verify get_table_html was called
    mock_get_table_html.assert_called_once()


@patch("src.notifier.get_table_html")
@patch("smtplib.SMTP")
def test_send_email_success_with_list(
    mock_smtp, mock_get_table_html, mock_config, sample_cars_list
):
    """Test successful email sending with list input."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_list)

    # Verify SMTP was called correctly
    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("test@example.com", "testpass")
    mock_smtp_instance.sendmail.assert_called_once()

    # Verify get_table_html was called with DataFrame (converted from list)
    mock_get_table_html.assert_called_once()
    called_df = mock_get_table_html.call_args[0][0]
    assert isinstance(called_df, pd.DataFrame)
    assert len(called_df) == 1
    assert called_df.iloc[0]["make"] == "Audi"


@patch("builtins.print")
def test_send_email_empty_dataframe(mock_print, mock_config):
    """Test sending email with empty DataFrame."""
    empty_df = pd.DataFrame()
    notifier = Notifier(mock_config)

    # Send email with empty data
    notifier.send_email("Test Subject", empty_df)

    # Should print "No cars to send." and return early
    mock_print.assert_called_with("No cars to send.")


@patch("builtins.print")
def test_send_email_empty_list(mock_print, mock_config):
    """Test sending email with empty list."""
    notifier = Notifier(mock_config)

    # Send email with empty data
    notifier.send_email("Test Subject", [])

    # Should print "No cars to send." and return early
    mock_print.assert_called_with("No cars to send.")


@patch("src.notifier.get_table_html")
@patch("smtplib.SMTP")
@patch("builtins.print")
def test_send_email_smtp_exception(
    mock_print, mock_smtp, mock_get_table_html, mock_config, sample_cars_df
):
    """Test email sending with SMTP exception."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")

    notifier = Notifier(mock_config)

    # Send email (should handle exception)
    notifier.send_email("Test Subject", sample_cars_df)

    # Should print error message
    mock_print.assert_any_call("Sending email...")
    mock_print.assert_any_call("Failed to send email: SMTP Error")


@patch("src.notifier.get_table_html")
@patch("smtplib.SMTP")
def test_send_email_message_content(
    mock_smtp, mock_get_table_html, mock_config, sample_cars_df
):
    """Test email message content and structure."""
    # Setup mocks
    mock_table_html = "<html><table>Test Table</table></html>"
    mock_get_table_html.return_value = mock_table_html
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_df)

    # Get the email message that was sent
    sendmail_call_args = mock_smtp_instance.sendmail.call_args[0]
    from_addr = sendmail_call_args[0]
    to_addr = sendmail_call_args[1]
    message_str = sendmail_call_args[2]

    # Verify email addresses
    assert from_addr == "test@example.com"
    assert to_addr == "recipient@example.com"

    # Verify message content
    assert "Subject: Test Subject" in message_str
    assert "From: test@example.com" in message_str
    assert "To: recipient@example.com" in message_str
    assert "Content-Type: text/html" in message_str


@patch("src.notifier.get_table_html")
@patch("smtplib.SMTP")
@patch("builtins.print")
def test_send_email_prints_status_messages(
    mock_print, mock_smtp, mock_get_table_html, mock_config, sample_cars_df
):
    """Test that appropriate status messages are printed."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_df)

    # Verify status messages
    mock_print.assert_any_call("Sending email...")
    mock_print.assert_any_call("Email sent successfully.")


def test_notifier_with_different_config():
    """Test notifier with different configuration."""
    different_config = MockConfig()
    different_config.email_settings = {
        "smtp_server": "different.smtp.com",
        "smtp_port": 465,
        "username": "different@example.com",
        "password": "differentpass",
        "recipient": "different_recipient@example.com",
    }

    notifier = Notifier(different_config)
    assert notifier.config.email_settings["smtp_server"] == "different.smtp.com"
    assert notifier.config.email_settings["smtp_port"] == 465
    assert notifier.config.email_settings["username"] == "different@example.com"
