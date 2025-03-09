"""config docstring."""


class Config:
    """clss"""

    def __init__(self):
        self.base_url = "https://www.autoscout24.com"
        self.filters = {
            "make": "Toyota",
            "model": "Corolla",
            "min_price": 5000,
            "max_price": 20000,
            "min_year": 2015,
            "max_year": 2022,
            # Add more filters as needed
        }
        self.email_settings = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "your_email@example.com",
            "password": "your_password",
            "recipient": "recipient@example.com",
        }
