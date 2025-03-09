"""Exporter module for handling car data export and import."""

import pandas as pd


class Exporter:
    """Class for exporting and importing car data."""

    def __init__(self, cars):
        """Initialize the Exporter with a list of cars.

        Args:
            cars (list): A list of car dictionaries to be exported.
        """
        self.cars = cars

    def export_to_csv(self, filename):
        """Export the list of cars to a CSV file.

        Args:
            filename (str): The name of the file to which the data will be exported.
        """
        # Use pandas to export the car data to a CSV file
        df = pd.DataFrame(self.cars)
        df.to_csv(filename, index=False)

    def import_from_csv(self, filename):
        """Import car data from a CSV file and return a list of car dictionaries.

        Args:
            filename (str): The name of the file from which the data will be imported.

        Returns:
            list: A list of car dictionaries imported from the CSV file.
        """
        # Read the CSV file into a DataFrame
        df = pd.read_csv(filename)
        # Convert the DataFrame to a list of dictionaries
        cars_list = df.to_dict(orient="records")
        return cars_list
