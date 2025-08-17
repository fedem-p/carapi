"""Module to calculate and rank cars based on several attributes."""

import os
import pandas as pd
from src.constants import WEIGHTS, FUEL_SCORES, FAVORITE_MODELS


class AutoScore:  # pylint: disable=too-many-instance-attributes
    """Class to calculate a score for cars based on various factors."""

    def __init__(self, folder_path):
        """Load all CSV files from a given folder and remove duplicates"""
        csv_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".csv")
        ]
        self.data = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
        self.data.drop_duplicates(subset=["url"], inplace=True)

        # Handle missing values appropriately based on data type
        # Fill numeric columns with 0 or sensible defaults
        numeric_columns = [
            "price",
            "mileage",
            "year",
            "vehicle_mileage",
            "seats",
            "doors",
            "previous_owner",
        ]
        for col in numeric_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors="coerce").fillna(
                    0
                )

        # Fill string columns with empty strings
        string_columns = [
            "fuel_type",
            "body_type",
            "emission_class",
            "make",
            "model",
            "warranty",
            "full_service_history",
            "non_smoker_vehicle",
            "power",
            "gearbox",
            "engine_size",
            "emission_sticker",
            "car_type",
            "country_version",
            "offer_number",
            "first_registration",
            "general_inspection",
        ]
        for col in string_columns:
            if col in self.data.columns:
                self.data[col] = self.data[col].fillna("")

        # Fill boolean columns with False
        boolean_columns = [
            "android_auto",
            "car_play",
            "cruise_control",
            "adaptive_cruise_control",
            "seat_heating",
        ]
        for col in boolean_columns:
            if col in self.data.columns:
                self.data[col] = self.data[col].fillna(False)

        self._calculate_ranges()

    def _calculate_ranges(self):
        """Determine min/max values for normalization"""
        self.price_min, self.price_max = (
            self.data["price"].min(),
            self.data["price"].max(),
        )
        self.mileage_min, self.mileage_max = (
            self.data["mileage"].min(),
            self.data["mileage"].max(),
        )

        def extract_power(x):
            """Extract power value from power string, handling edge cases."""
            if not x or str(x).strip() == "":
                return 0
            try:
                parts = str(x).split()
                if parts and parts[0].isdigit():
                    return int(parts[0])
                return 0
            except (ValueError, IndexError):
                return 0

        self.power_min, self.power_max = (
            self.data["power"].apply(extract_power).min(),
            self.data["power"].apply(extract_power).max(),
        )
        self.year_min, self.year_max = self.data["year"].min(), self.data["year"].max()

    def normalize(self, value, min_val, max_val):
        """Normalize numerical values between 0 and 1"""
        return (
            1 - abs(value - min_val) / (max_val - min_val) if max_val > min_val else 1
        )

    def score_car(self, car):
        """Compute the total score for a single car entry"""
        score = 0

        # Price score (normalized) - handle None values
        if car.get("price") is not None:
            score += WEIGHTS["price"] * self.normalize(
                car["price"], self.price_min, self.price_max
            )

        # Mileage score (normalized) - handle None values
        if car.get("mileage") is not None:
            score += WEIGHTS["mileage"] * self.normalize(
                car["mileage"], self.mileage_min, self.mileage_max
            )

        # Fuel Type Matching - handle None/empty values
        fuel_type = car.get("fuel_type", "")
        if fuel_type:
            fuel_score = FUEL_SCORES.get(fuel_type.lower(), 0)
            score += WEIGHTS["fuel_type"] * fuel_score

        # Features (Android Auto & CarPlay) - already boolean after cleaning
        if car.get("android_auto") and car.get("car_play"):
            score += WEIGHTS["features"]

        # Adaptive Cruise Control - already boolean after cleaning
        if car.get("adaptive_cruise_control"):
            score += WEIGHTS["adaptive_cruise"]

        # Seat Heating - already boolean after cleaning
        if car.get("seat_heating"):
            score += WEIGHTS["seat_heating"]

        # Power (normalized) - handle None/empty values
        power_str = car.get("power", "")
        power_hp = 0
        if power_str:
            try:
                parts = power_str.split()
                if parts and parts[0].isdigit():
                    power_hp = int(parts[0])
            except (ValueError, IndexError):
                power_hp = 0
        score += WEIGHTS["power"] * self.normalize(
            power_hp, self.power_min, self.power_max
        )

        # Registration Year (normalized) - handle None values
        if car.get("year") is not None:
            score += WEIGHTS["registration_year"] * self.normalize(
                car["year"], self.year_min, self.year_max
            )

        # Body Type - handle None/empty values
        body_type = car.get("body_type", "")
        if body_type and body_type.lower() in [
            "station wagon",
            "off-road/pick-up",
            "sedan",
        ]:
            score += WEIGHTS["body_type"]

        # Emissions - handle None/empty values
        emission_class = car.get("emission_class", "")
        if emission_class:
            emission_lower = emission_class.lower()
            if "6" in emission_lower:
                score += WEIGHTS["emissions"]
            elif "5" in emission_lower:
                score += WEIGHTS["emissions"] * 0.8

        # Coolness Factor - handle None/empty values
        make = car.get("make", "")
        model = car.get("model", "")
        if make and model:
            make_lower = make.lower()
            model_lower = model.lower()
            if (make_lower, model_lower) in FAVORITE_MODELS or (
                make_lower in [make for make, _ in FAVORITE_MODELS]
                and model_lower == "x"
            ):
                score += WEIGHTS["coolness_factor"]

        # Warranty Bonus - handle None/empty values
        warranty = car.get("warranty", "")
        if warranty and "no" not in warranty.lower():
            score += WEIGHTS["warranty"]

        # Previous Owners - handle None values
        previous_owner = car.get("previous_owner")
        if previous_owner == 1:
            score += previous_owner
        elif previous_owner == 2:
            score += previous_owner * 0.75

        # Service & Non-Smoker History Penalty - handle None/empty values
        full_service_history = car.get("full_service_history", "")
        if full_service_history and "no" in full_service_history.lower():
            score -= 2

        non_smoker_vehicle = car.get("non_smoker_vehicle", "")
        if non_smoker_vehicle and "no" in non_smoker_vehicle.lower():
            score -= 1

        return score

    def assign_grade(self, score):
        """Assign a grade based on the car's score."""
        if score > 28:
            return "Outstanding"  # New category for top-tier cars
        if 24 < score <= 28:
            return "Excellent"
        if 19 < score <= 24:
            return "Good"
        if 14 < score <= 19:
            return "Decent"
        if 9 < score <= 14:
            return "Not Good"
        return "Bad"

    def rank_cars(self, n=10):
        """Score and rank cars."""
        self.data["score"] = self.data.apply(self.score_car, axis=1)
        self.data["score"] = self.data["score"].round(1)

        # Apply the grade function
        self.data["grade"] = self.data["score"].apply(self.assign_grade)

        # Sort cars by score
        sorted_data = self.data.sort_values(by="score", ascending=False)

        # Get unique make-model combinations first
        unique_cars = sorted_data.drop_duplicates(subset=["make", "model"])
        if len(unique_cars) >= n:
            return unique_cars.head(n)

        # Fill remaining spots with duplicates if necessary
        remaining_cars = sorted_data[~sorted_data.index.isin(unique_cars.index)]
        final_selection = pd.concat(
            [unique_cars, remaining_cars.head(n - len(unique_cars))], ignore_index=True
        )

        return final_selection
