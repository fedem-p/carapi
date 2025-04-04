"""Module to fetch car brands and models from the autoscout api."""

import csv
import requests
from src.constants import CSV_FILE_PATH, FILTER_MAKES


def fetch_makes_and_models():
    """Fetch makes and models from the AutoScout24 API."""
    url = "https://listing-creation.api.autoscout24.com/makes?culture=de-DE&marketplace=de"
    response = requests.get(url, headers={"accept": "application/json"}, timeout=10)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()


def save_makes_to_csv(data, filename=CSV_FILE_PATH):
    """Save the makes and models data to a CSV file, excluding specified makes."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["make_id", "make_name", "model_id", "model_name"])  # Header
        for make in data["makes"]:
            make_id = make["id"]
            make_name = make["name"]
            # Check if the make is in the include list
            if make_name not in FILTER_MAKES:
                continue  # Skip this make if not
            # Check if 'models' key exists and iterate over models
            if "models" in make:
                for model in make["models"]:
                    model_id = model["id"]
                    model_name = model["name"]
                    writer.writerow([make_id, make_name, model_id, model_name])
            else:
                # If there are no models, write the make with empty model fields
                writer.writerow([make_id, make_name, "", ""])


def load_makes_from_csv(filename=CSV_FILE_PATH):
    """Load makes from the CSV file and return a mapping of make names to their IDs."""
    makes_mapping = {}  # Dictionary to hold make name and ID mapping
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            make_name = row["make_name"]
            make_id = row["make_id"]
            if make_name:  # Ensure make name is not empty
                makes_mapping[make_name.lower()] = (
                    make_id  # Store in lowercase for case-insensitive access
                )

    return makes_mapping  # Return the mapping


def main():
    """Main function to fetch, save makes and models, and list makes."""
    makes_data = fetch_makes_and_models()
    save_makes_to_csv(makes_data)
    print(f"Successfully saved makes and models to '{CSV_FILE_PATH}'.")


if __name__ == "__main__":
    main()
