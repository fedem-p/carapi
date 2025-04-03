import pandas as pd
import os
from .constants import WEIGHTS, FUEL_SCORES, FAVORITE_MODELS

class AutoScore:
    def __init__(self, folder_path):
        """Load all CSV files from a given folder and remove duplicates"""
        csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
        self.data = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
        self.data.drop_duplicates(subset=['url'], inplace=True)
        self.data.fillna('', inplace=True)  # Handle missing values by replacing with an empty string
        self._calculate_ranges()
    
    def _calculate_ranges(self):
        """Determine min/max values for normalization"""
        self.price_min, self.price_max = self.data['price'].min(), self.data['price'].max()
        self.mileage_min, self.mileage_max = self.data['mileage'].min(), self.data['mileage'].max()
        self.power_min, self.power_max = self.data['power'].apply(lambda x: int(str(x).split()[0]) if str(x).split()[0].isdigit() else 0).min(), self.data['power'].apply(lambda x: int(str(x).split()[0]) if str(x).split()[0].isdigit() else 0).max()
        self.year_min, self.year_max = self.data['year'].min(), self.data['year'].max()
    
    def normalize(self, value, min_val, max_val):
        """Normalize numerical values between 0 and 1"""
        return 1 - abs(value - min_val) / (max_val - min_val) if max_val > min_val else 1

    def score_car(self, car):
        """Compute the total score for a single car entry"""
        score = 0
        
        # Price score (normalized)
        score += WEIGHTS['price'] * self.normalize(car['price'], self.price_min, self.price_max)
        
        # Mileage score (normalized)
        score += WEIGHTS['mileage'] * self.normalize(car['mileage'], self.mileage_min, self.mileage_max)
        
        # Fuel Type Matching
        fuel_score = FUEL_SCORES.get(car['fuel_type'].lower(), 0)
        score += WEIGHTS['fuel_type'] * fuel_score
        
        # Features (Android Auto & CarPlay)
        if car['android_auto'] and car['car_play']:
            score += WEIGHTS['features']
        
        # Adaptive Cruise Control
        if car['adaptive_cruise_control']:
            score += WEIGHTS['adaptive_cruise']

        # Seat Heating
        if car['seat_heating']:
            score += WEIGHTS['seat_heating']
        
        # Power (normalized)
        power_hp = int(car['power'].split()[0]) if car['power'] and car['power'].split()[0].isdigit() else 0
        score += WEIGHTS['power'] * self.normalize(power_hp, self.power_min, self.power_max)
        
        # Registration Year (normalized)
        score += WEIGHTS['registration_year'] * self.normalize(int(car['year']), self.year_min, self.year_max)
        
        # Body Type
        if car['body_type'].lower() in ['station wagon', 'off-road/pick-up', 'sedan']:
            score += WEIGHTS['body_type']
        
        # Emissions
        if '6' in car['emission_class'].lower():
            score += WEIGHTS['emissions']
        elif '5' in car['emission_class'].lower():
            score += WEIGHTS['emissions'] * 0.8
        
        # Coolness Factor
        if (car['make'].lower(), car['model'].lower()) in FAVORITE_MODELS or (car['make'].lower() in [make for make, _ in FAVORITE_MODELS] and car['model'].lower() == 'x'):
            score += WEIGHTS['coolness_factor']
        
        # Warranty Bonus
        if "no" not in car['warranty'].lower():
            score += WEIGHTS['warranty']
        
        # Previous Owners
        if car['previous_owner'] == 1:
            score += car['previous_owner']
        elif car['previous_owner'] == 2:
            score += car['previous_owner'] * 0.75
        
        # Service & Non-Smoker History Penalty
        if "no" in car['full_service_history'].lower():
            score -= 2
        if "no" in car['non_smoker_vehicle'].lower():
            score -= 1

        return score
    
    def assign_grade(self, score):
        """Assign a grade based on the car's score."""
        if score > 28:
            return "Outstanding"  # New category for top-tier cars
        elif 24 < score <= 28:
            return "Excellent"
        elif 19 < score <= 24:
            return "Good"
        elif 14 < score <= 19:
            return "Decent"
        elif 9 < score <= 14:
            return "Not Good"
        else:
            return "Bad"
    
    def rank_cars(self, n=10):
        """Score and rank cars, ensuring unique make-model combinations first and adding a grade column."""
        self.data['score'] = self.data.apply(self.score_car, axis=1)
        self.data['score'] = self.data['score'].round(1)
        
        # Apply the grade function
        self.data['grade'] = self.data['score'].apply(self.assign_grade)

        # Sort cars by score
        sorted_data = self.data.sort_values(by='score', ascending=False)

        # Get unique make-model combinations first
        unique_cars = sorted_data.drop_duplicates(subset=['make', 'model'])
        if len(unique_cars) >= n:
            return unique_cars.head(n)

        # Fill remaining spots with duplicates if necessary
        remaining_cars = sorted_data[~sorted_data.index.isin(unique_cars.index)]
        final_selection = pd.concat([unique_cars, remaining_cars.head(n - len(unique_cars))])

        return final_selection
