"""Getting started."""

import argparse
import os
from src.config import Config
from src.scraper import Scraper
from src.exporter import Exporter
from src.auto_score import AutoScore
from src.notifier import Notifier  # pylint: disable=unused-import


def main():
    """
    Main function to execute the scraping, exporting, and analysis of car listings.

    This function:
    1. Loads the configuration.
    2. Scrapes car data with different sorting methods.
    3. Exports the scraped data to CSV files.
    4. Analyzes the data by ranking cars based on a calculated score.
    5. Prints the top-ranked cars with relevant details.
    """
    parser = argparse.ArgumentParser(description="Car listings scraper and analyzer")
    parser.add_argument(
        "--email", action="store_true", help="Send email notification with top cars"
    )
    parser.add_argument(
        "--settings", type=str, help="Path to settings JSON file (default: settings.json)"
    )
    args = parser.parse_args()

    # Check environment variable as well as flag
    send_email_env = os.environ.get("SEND_EMAIL", "false").lower() == "true"
    send_email = args.email or send_email_env

    print(f"Send email notifications: {send_email}")

    # Load configuration
    config = Config(settings_path=args.settings)

    # Scrape data
    scraper = Scraper(config)

    for sort in ["standard", "price", "age"]:
        print(f"================ Scraping with sorting: {sort} ================")
        cars = scraper.scrape_data(sort_method=sort)

        # (No separate processing step needed since filtering is done in the scraper)

        # Export data to CSV
        exporter = Exporter(cars)
        exporter.export_to_csv(f"data/results/filtered_cars_{sort}.csv")

    ## Analyse data
    autoscorer = AutoScore("data/results")
    ranked_cars = autoscorer.rank_cars(n=20)
    print(
        ranked_cars[
            ["make", "model", "price", "mileage", "year", "score", "grade", "url"]
        ].to_string()
    )

    # Send email with the top cars if --email flag or SEND_EMAIL env is set
    if send_email:
        notifier = Notifier(config)
        notifier.send_email("Latest Car Listings", ranked_cars)


if __name__ == "__main__":
    main()
