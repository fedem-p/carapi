import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Notifier:
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

        # Select relevant columns
        columns = [
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
        cars_df = cars_df[columns]

        # Convert URL to clickable links
        cars_df["url"] = cars_df["url"].apply(lambda x: f'<a href="{x}">Link</a>')

        # Format the table with embedded images
        table_html = """
        <html>
        <body>
        <h2>Latest Car Listings</h2>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr>
                <th>Make</th>
                <th>Model</th>
                <th>Price</th>
                <th>Mileage</th>
                <th>Year</th>
                <th>Score</th>
                <th>Grade</th>
                <th>Listing</th>
                <th>Image</th>
            </tr>
        """

        for _, row in cars_df.iterrows():
            highlight_style = "background-color: yellow;" if row["score"] > 24 else ""
            table_html += f"""
            <tr style="{highlight_style}">
                <td>{row['make']}</td>
                <td>{row['model']}</td>
                <td>{row['price']}</td>
                <td>{row['mileage']}</td>
                <td>{row['year']}</td>
                <td>{row['score']}</td>
                <td>{row['grade']}</td>
                <td>{row['url']}</td>
                <td><img src="{row['img_url']}" width="100"></td>
            </tr>
            """

        table_html += """
        </table>
        </body>
        </html>
        """

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
            ) as server:
                server.starttls()
                server.login(
                    self.config.email_settings["username"],
                    self.config.email_settings["password"],
                )
                server.sendmail(
                    self.config.email_settings["username"],
                    self.config.email_settings["recipient"],
                    msg.as_string(),
                )
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")
