"""noftifuer docstring."""

import smtplib


class Notifier:
    """class"""

    def __init__(self, config):
        """_summary_

        Args:
            config (_type_): _description_
        """
        self.config = config

    def send_email(self, subject, body):
        """_summary_

        Args:
            subject (_type_): _description_
            body (_type_): _description_
        """
        # Use smtplib to send an email with the car listings
        with smtplib.SMTP(
            self.config.email_settings["smtp_server"],
            self.config.email_settings["smtp_port"],
        ) as server:
            server.starttls()
            server.login(
                self.config.email_settings["username"],
                self.config.email_settings["password"],
            )
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(
                self.config.email_settings["username"],
                self.config.email_settings["recipient"],
                message,
            )
