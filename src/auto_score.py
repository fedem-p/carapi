"""Module to calculate and rank cars based on several attributes."""

import os
import pandas as pd
from src.config import Config


BEST_CARS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "best", "best_cars.csv"
)


def save_best_cars(top_cars, max_rows=300, best_cars_file=None):
    """Save top cars to BEST_CARS_FILE, keeping only max_rows, deduplicated and sorted by score."""
    if best_cars_file is None:
        best_cars_file = BEST_CARS_FILE
    best_dir = os.path.dirname(best_cars_file)
    os.makedirs(best_dir, exist_ok=True)
    if os.path.exists(best_cars_file):
        existing = pd.read_csv(best_cars_file)
        combined = pd.concat([existing, top_cars], ignore_index=True)
        # Remove duplicates by url, keep best score
        combined["score"] = combined.apply(
            lambda row: row["score"] if "score" in row else 0, axis=1
        )
        combined = combined.sort_values(by="score", ascending=False)
        combined = combined.drop_duplicates(subset=["url"], keep="first")
        combined = combined.head(max_rows)
        combined.to_csv(best_cars_file, index=False)
    else:
        # If file doesn't exist, just save the top cars (clip if needed)
        top_cars = top_cars.sort_values(by="score", ascending=False).head(max_rows)
        top_cars.to_csv(best_cars_file, index=False)


class AutoScore:  # pylint: disable=too-many-instance-attributes
    """Class to calculate a score for cars based on various factors."""

    def __init__(self, folder_path, profile="standard"):
        """Load all CSV files from a given folder and remove duplicates."""
        csv_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".csv")
        ]
        self.data = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
        self.data.drop_duplicates(subset=["url"], inplace=True)
        self.data.fillna(
            "", inplace=True
        )  # Handle missing values by replacing with an empty string
        self.config = Config()
        self.profile = profile
        self.weights = self.config.scoring_profiles[profile]["weights"]
        self.fuel_scores = self.config.scoring_profiles[profile]["fuel_scores"]
        self.favorite_models = self.config.scoring_profiles[profile]["favorite_models"]
        self._calculate_ranges()

    def _calculate_ranges(self):
        """Determine min/max values for normalization."""
        self.price_min, self.price_max = (
            self.data["price"].min(),
            self.data["price"].max(),
        )
        self.mileage_min, self.mileage_max = (
            self.data["mileage"].min(),
            self.data["mileage"].max(),
        )
        self.power_min = (
            self.data["power"]
            .apply(
                lambda x: int(str(x).split()[0]) if str(x).split()[0].isdigit() else 0
            )
            .min()
        )
        self.power_max = (
            self.data["power"]
            .apply(
                lambda x: int(str(x).split()[0]) if str(x).split()[0].isdigit() else 0
            )
            .max()
        )
        self.year_min, self.year_max = self.data["year"].min(), self.data["year"].max()

    def normalize(self, value, min_val, max_val):
        """Normalize numerical values between 0 and 1."""
        if max_val > min_val:
            return 1 - abs(value - min_val) / (max_val - min_val)
        return 1

    def score_car(self, car):
        """Compute the total score for a single car entry"""
        score = 0

        # Price score (normalized)
        score += self.weights["price"] * self.normalize(
            car["price"], self.price_min, self.price_max
        )

        # Mileage score (normalized)
        score += self.weights["mileage"] * self.normalize(
            car["mileage"], self.mileage_min, self.mileage_max
        )

        # Fuel Type Matching
        fuel_score = self.fuel_scores.get(car["fuel_type"].lower(), 0)
        score += self.weights["fuel_type"] * fuel_score

        # Features (Android Auto & CarPlay)
        if car["android_auto"] and car["car_play"]:
            score += self.weights["features"]

        # Adaptive Cruise Control
        if car["adaptive_cruise_control"]:
            score += self.weights["adaptive_cruise"]

        # Seat Heating
        if car["seat_heating"]:
            score += self.weights["seat_heating"]

        # Power (normalized)
        power_hp = (
            int(car["power"].split()[0])
            if car["power"] and car["power"].split()[0].isdigit()
            else 0
        )
        score += self.weights["power"] * self.normalize(
            power_hp, self.power_min, self.power_max
        )

        # Registration Year (normalized)
        score += self.weights["registration_year"] * self.normalize(
            int(car["year"]), self.year_min, self.year_max
        )

        # Body Type
        if car["body_type"].lower() in ["station wagon", "off-road/pick-up", "sedan"]:
            score += self.weights["body_type"]

        # Emissions
        if "6" in car["emission_class"].lower():
            score += self.weights["emissions"]
        elif "5" in car["emission_class"].lower():
            score += self.weights["emissions"] * 0.8

        # Coolness Factor
        if (car["make"].lower(), car["model"].lower()) in self.favorite_models or (
            car["make"].lower() in [make for make, _ in self.favorite_models]
            and car["model"].lower() == "x"
        ):
            score += self.weights["coolness_factor"]

        # Warranty Bonus
        if "no" not in car["warranty"].lower():
            score += self.weights["warranty"]

        # Previous Owners
        if car["previous_owner"] == 1:
            score += car["previous_owner"]
        elif car["previous_owner"] == 2:
            score += car["previous_owner"] * 0.75

        # Service & Non-Smoker History Penalty
        if "no" in car["full_service_history"].lower():
            score -= 2
        if "no" in car["non_smoker_vehicle"].lower():
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

    def _score_and_rank_data(self, data, n=10):
        """Helper method to score, grade, and rank car data."""
        data = data.copy()
        data["score"] = data.apply(self.score_car, axis=1)
        data["score"] = data["score"].round(1)
        data["grade"] = data["score"].apply(self.assign_grade)

        # Sort cars by score
        sorted_data = data.sort_values(by="score", ascending=False)

        # Get unique make-model combinations first
        unique_cars = sorted_data.drop_duplicates(subset=["make", "model"])
        return unique_cars.head(n)

    def rank_cars(self, n=10, save=True):
        """Score and rank cars. Optionally save top cars to /data/best/ folder."""
        top_cars = self._score_and_rank_data(self.data, n)

        if save:
            save_best_cars(top_cars)

        return top_cars

    def get_all_time_best(self, n=10):
        """Return the all-time best cars using existing scores only."""
        if not os.path.exists(BEST_CARS_FILE):
            raise FileNotFoundError("No best cars file found.")
        all_best = pd.read_csv(BEST_CARS_FILE)
        # Only use the existing score column, do not recalculate
        if "score" not in all_best.columns:
            raise ValueError("No score column found in best cars file.")
        all_best = all_best.copy()
        all_best["score"] = all_best["score"].round(1)
        sorted_data = all_best.sort_values(by="score", ascending=False)
        unique_cars = sorted_data.drop_duplicates(subset=["make", "model"])
        return unique_cars.head(n)
