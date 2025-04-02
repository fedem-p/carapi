"""Getting started."""

from .config import Config
from .scraper import Scraper
from .exporter import Exporter
from .auto_score import AutoScore


# main.py
def main():
    # Load configuration
    config = Config()

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
    autoscorer = AutoScore('data/results')
    ranked_cars = autoscorer.rank_cars(n = 20)
    print(ranked_cars[['make', 'model', 'price', 'mileage', 'year', 'score', 'grade', 'url']].to_string())

    # # (Later) Send email with the top cars
    # notifier = Notifier(config)
    # email_body = "\n".join([f"{car['make']} {car['model']} - €{car['price']}" for car in cars])
    # notifier.send_email("Filtered Car Listings", email_body)


if __name__ == "__main__":
    main()
