"""exporter docstring."""

import pandas as pd


class Exporter:
    """class"""

    def __init__(self, cars):
        """_summary_

        Args:
            cars (_type_): _description_
        """
        self.cars = cars

    def export_to_csv(self, filename):
        """_summary_

        Args:
            filename (_type_): _description_
        """
        # Use pandas to export the car data to a CSV file
        df = pd.DataFrame(self.cars)
        df.to_csv(filename, index=False)
