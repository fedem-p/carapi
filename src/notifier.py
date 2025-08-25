"""Handles sending notifications via email, including formatting and sending car listings."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.table_utils import get_table_html


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
            cars_df (pd.DataFrame): DataFrame containing car details.
        """
        if cars_df.empty:
            print("No cars to send.")
            return

        # Generate HTML table for the car listings
        table_html = get_table_html(cars_df)

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = self.config.email_settings["username"]
        msg["To"] = self.config.email_settings["recipient"]
        msg["Subject"] = subject

        # Attach table as email body in HTML format
        msg.attach(MIMEText(table_html, "html"))

        # Send email
        print("Sending email...")
        try:
            with smtplib.SMTP(
                self.config.email_settings["smtp_server"],
                self.config.email_settings["smtp_port"],
            ) as smtp:
                smtp.starttls()
                smtp.login(
                    self.config.email_settings["username"],
                    self.config.email_settings["password"],
                )
                smtp.sendmail(
                    self.config.email_settings["username"],
                    self.config.email_settings["recipient"],
                    msg.as_string(),
                )
            print("Email sent successfully.")
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")
