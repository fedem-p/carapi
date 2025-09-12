"""Handles sending notifications via email, including formatting and sending car listings."""

import mailtrap as mt  # type: ignore
import pandas as pd
from src.table_utils import get_table_html

EMAIL_SIZE_MB = 1_000_000
MAX_EMAIL_SIZE = 10 * EMAIL_SIZE_MB  # 10MB


class Notifier:  # pylint: disable=too-few-public-methods
    """Handles sending notifications via email."""

    def __init__(self, config):
        """
        Initializes the Notifier with configuration settings.

        Args:
            config (object): Configuration object containing email settings.
        """
        self.config = config

    def send_email(self, subject, cars_df):
        """
        Sends an email with a formatted list of car listings.

        Args:
            subject (str): The email subject.
            cars_df (pd.DataFrame or list): Car details as DataFrame or list of dicts.
        """
        if isinstance(cars_df, list):
            cars_df = pd.DataFrame(cars_df)
        if cars_df.empty:
            print("No cars to send.")
            return  # No cars to send

        # Generate HTML table for the car listings
        table_html = get_table_html(cars_df)
        mail = mt.Mail(
            sender=mt.Address(email=self.config.email_settings["sender"]),
            to=[mt.Address(email=self.config.email_settings["recipient"])],
            subject=subject,
            html=table_html,
            category="Car Listings",
        )

        # Check email size before sending
        email_size = len(table_html.encode("utf-8"))
        print(f"Email size: {email_size / EMAIL_SIZE_MB:.2f} MB")
        if email_size > MAX_EMAIL_SIZE:
            raise ValueError("Email size exceeds 10MB. Email not sent.")

        print("Creating Mailtrap client...")
        try:
            client = mt.MailtrapClient(token=self.config.email_settings["api_key"])
        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to create Mailtrap client: {type(e).__name__}: {e}")
            raise

        print("Sending email via Mailtrap...")
        try:
            client.send(mail)
        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to send email via Mailtrap: {type(e).__name__}: {e}")
