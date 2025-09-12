"""Tests for the notifier module."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.notifier import Notifier


class MockConfig:
    """Mock configuration for testing."""

    def __init__(self):
        self.email_settings = {
            "recipient": "recipient@example.com",
            "sender": "test@example.com",
            "api_key": "test-api-key",
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
@patch("src.notifier.mt.MailtrapClient")
@patch("src.notifier.mt.Mail")
@patch("src.notifier.mt.Address")
def test_send_email_success_with_dataframe(
    mock_address,
    mock_mail,
    mock_mailtrap_client,
    mock_get_table_html,
    mock_config,
    sample_cars_df,
):
    """Test successful email sending with DataFrame input."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_client_instance = MagicMock()
    mock_mailtrap_client.return_value = mock_client_instance
    mock_mail_instance = MagicMock()
    mock_mail.return_value = mock_mail_instance
    mock_address_instance = MagicMock()
    mock_address.return_value = mock_address_instance

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_df)

    # Verify Mailtrap client was created correctly
    mock_mailtrap_client.assert_called_once_with(token="test-api-key")

    # Verify Mail object was created
    mock_mail.assert_called_once()

    # Verify client.send was called
    mock_client_instance.send.assert_called_once_with(mock_mail_instance)

    # Verify get_table_html was called
    mock_get_table_html.assert_called_once()


@patch("src.notifier.get_table_html")
@patch("src.notifier.mt.MailtrapClient")
@patch("src.notifier.mt.Mail")
@patch("src.notifier.mt.Address")
def test_send_email_success_with_list(
    mock_address,
    mock_mail,
    mock_mailtrap_client,
    mock_get_table_html,
    mock_config,
    sample_cars_list,
):
    """Test successful email sending with list input."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_client_instance = MagicMock()
    mock_mailtrap_client.return_value = mock_client_instance
    mock_mail_instance = MagicMock()
    mock_mail.return_value = mock_mail_instance
    mock_address_instance = MagicMock()
    mock_address.return_value = mock_address_instance

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_list)

    # Verify Mailtrap client was created correctly
    mock_mailtrap_client.assert_called_once_with(token="test-api-key")

    # Verify client.send was called
    mock_client_instance.send.assert_called_once_with(mock_mail_instance)

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
@patch("src.notifier.mt.MailtrapClient")
@patch("builtins.print")
def test_send_email_smtp_exception(
    mock_print, mock_mailtrap_client, mock_get_table_html, mock_config, sample_cars_df
):
    """Test email sending with Mailtrap exception."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_mailtrap_client.side_effect = Exception("Mailtrap Error")

    notifier = Notifier(mock_config)

    # Send email (should handle exception)
    with pytest.raises(Exception):
        notifier.send_email("Test Subject", sample_cars_df)

    # Should print error message
    mock_print.assert_any_call("Creating Mailtrap client...")
    mock_print.assert_any_call(
        "Failed to create Mailtrap client: Exception: Mailtrap Error"
    )


@patch("src.notifier.get_table_html")
@patch("src.notifier.mt.MailtrapClient")
@patch("src.notifier.mt.Mail")
@patch("src.notifier.mt.Address")
def test_send_email_message_content(
    mock_address,
    mock_mail,
    mock_mailtrap_client,
    mock_get_table_html,
    mock_config,
    sample_cars_df,
):
    """Test email message content and structure."""
    # Setup mocks
    mock_table_html = "<html><table>Test Table</table></html>"
    mock_get_table_html.return_value = mock_table_html
    mock_client_instance = MagicMock()
    mock_mailtrap_client.return_value = mock_client_instance
    mock_mail_instance = MagicMock()
    mock_mail.return_value = mock_mail_instance

    # Setup Address mock to return different instances for sender and recipient
    mock_sender_address = MagicMock()
    mock_recipient_address = MagicMock()
    mock_address.side_effect = [mock_sender_address, mock_recipient_address]

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_df)

    # Verify Mail object was created with correct parameters
    mock_mail.assert_called_once_with(
        sender=mock_sender_address,
        to=[mock_recipient_address],
        subject="Test Subject",
        html=mock_table_html,
        category="Car Listings",
    )

    # Verify Address objects were created with correct emails
    mock_address.assert_any_call(email="test@example.com")
    mock_address.assert_any_call(email="recipient@example.com")


@patch("src.notifier.get_table_html")
@patch("src.notifier.mt.MailtrapClient")
@patch("src.notifier.mt.Mail")
@patch("src.notifier.mt.Address")
@patch("builtins.print")
def test_send_email_prints_status_messages(
    mock_print,
    mock_address,
    mock_mail,
    mock_mailtrap_client,
    mock_get_table_html,
    mock_config,
    sample_cars_df,
):
    """Test that appropriate status messages are printed."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_client_instance = MagicMock()
    mock_mailtrap_client.return_value = mock_client_instance
    mock_mail_instance = MagicMock()
    mock_mail.return_value = mock_mail_instance
    mock_address_instance = MagicMock()
    mock_address.return_value = mock_address_instance

    notifier = Notifier(mock_config)

    # Send email
    notifier.send_email("Test Subject", sample_cars_df)

    # Verify status messages (the actual messages from the updated notifier)
    mock_print.assert_any_call("Creating Mailtrap client...")
    mock_print.assert_any_call("Sending email via Mailtrap...")
    # Check that email size is printed (format: "Email size: X.XX MB")
    email_size_calls = [
        call for call in mock_print.call_args_list if "Email size:" in str(call)
    ]
    assert len(email_size_calls) > 0


def test_notifier_with_different_config():
    """Test notifier with different configuration."""
    different_config = MockConfig()
    different_config.email_settings = {
        "sender": "different@example.com",
        "recipient": "different_recipient@example.com",
        "api_key": "different-api-key",
    }

    notifier = Notifier(different_config)
    assert notifier.config.email_settings["sender"] == "different@example.com"
    assert (
        notifier.config.email_settings["recipient"] == "different_recipient@example.com"
    )
    assert notifier.config.email_settings["api_key"] == "different-api-key"


@patch("src.notifier.get_table_html")
def test_send_email_size_limit(mock_get_table_html, mock_config, sample_cars_df):
    """Test email size limit check."""
    # Create a very large HTML string to exceed the 10MB limit
    large_html = "x" * (11 * 1_000_000)  # 11MB
    mock_get_table_html.return_value = large_html

    notifier = Notifier(mock_config)

    # Should raise ValueError for oversized email
    with pytest.raises(ValueError, match="Email size exceeds 10MB. Email not sent."):
        notifier.send_email("Test Subject", sample_cars_df)


@patch("src.notifier.get_table_html")
@patch("src.notifier.mt.MailtrapClient")
@patch("src.notifier.mt.Mail")
@patch("src.notifier.mt.Address")
@patch("builtins.print")
def test_send_email_send_exception(
    mock_print,
    mock_address,
    mock_mail,
    mock_mailtrap_client,
    mock_get_table_html,
    mock_config,
    sample_cars_df,
):
    """Test email sending with send exception."""
    # Setup mocks
    mock_get_table_html.return_value = "<html><table>Test Table</table></html>"
    mock_client_instance = MagicMock()
    mock_mailtrap_client.return_value = mock_client_instance
    mock_client_instance.send.side_effect = Exception("Send Error")
    mock_mail_instance = MagicMock()
    mock_mail.return_value = mock_mail_instance
    mock_address_instance = MagicMock()
    mock_address.return_value = mock_address_instance

    notifier = Notifier(mock_config)

    # Send email (should handle exception without raising)
    notifier.send_email("Test Subject", sample_cars_df)

    # Should print error message
    mock_print.assert_any_call("Sending email via Mailtrap...")
    mock_print.assert_any_call(
        "Failed to send email via Mailtrap: Exception: Send Error"
    )
