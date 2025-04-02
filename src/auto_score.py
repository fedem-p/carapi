import pandas as pd
import os

# Define weight for each attribute
WEIGHTS = {
    "make_model": 4,
    "price": 4,
    "mileage": 3,
    "fuel_type": 3,
    "features": 3,
    "adaptive_cruise": 2,
    "power": 1,
    "registration_year": 3,
    "body_type": 2,
    "emissions": 3,
    "coolness_factor": 2,
    "warranty": 3,
    "seat_heating": 2
}

FUEL_SCORES = {
    "Electric/Diesel": 1.0,
    "Electric/Gasoline": 0.9,
    "Diesel": 0.8,
    "Gasoline": 0.7,
    "Super 95": 0.7,
    "Regular/Benzine 91": 0.7
}

FAVORITE_MODELS = [
    ('skoda', 'superb'),
    ('skoda', 'octavia'),
    ('skoda', 'kamiq'),
    ('audi', 'x'),
    ('seat', 'ateca'),
    ('cupra', 'x'),
    ('bmw', 'x'),
    ('ford', 'explorer'),
    ('jaguar', 'x'),
    ('lexus', 'x'),
    ('maserati', 'x'),
    ('mazda', '6'),
    ('mercedes-benz', 'x'),
    ('porsche', 'x'),
    ('toyota', 'rav 4'),
    ('toyota', 'camry'),
    ('toyota', 'prius'),
    ('toyota', 'yaris cross'),
    ('volkswagen', 'arteon'),
    ('volkswagen', 'tiguan'),
    ('volkswagen', 'golf gti')
    
    # Add more favorite make-model combinations as needed
]

class AutoScore:
    def __init__(self, folder_path):
        """Load all CSV files from a given folder and remove duplicates"""
        csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
        self.data = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
        self.data.drop_duplicates(subset=['url'], inplace=True)
        self._calculate_ranges()
    
    def _calculate_ranges(self):
        """Determine min/max values for normalization"""
        self.price_min, self.price_max = self.data['price'].min(), self.data['price'].max()
        self.mileage_min, self.mileage_max = self.data['mileage'].min(), self.data['mileage'].max()
        self.power_min, self.power_max = self.data['power'].apply(lambda x: int(str(x).split()[0])).min(), self.data['power'].apply(lambda x: int(str(x).split()[0])).max()
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

        if car['seat_heating']:
            score += WEIGHTS['seat_heating']
        
        # Power (normalized)
        power_hp = int(car['power'].split()[0])
        score += WEIGHTS['power'] * self.normalize(power_hp, self.power_min, self.power_max)
        
        # Registration Year (normalized)
        score += WEIGHTS['registration_year'] * self.normalize(int(car['year']), self.year_min, self.year_max)
        
        # Body Type
        if car['body_type'].lower() in ['Station wagon', 'Off-Road/Pick-up', 'Sedan']:
            score += WEIGHTS['body_type']
        
        # Emissions
        if '6' in car['emission_class'].lower():
            score += WEIGHTS['emissions']
        elif '5' in car['emission_class'].lower():
            score += WEIGHTS['emissions'] * 0.8
        
        # Coolness Factor (Special Bonus for Selected Models)
        if (car['make'].lower(), car['model'].lower()) in FAVORITE_MODELS or (car['make'].lower() in [make for make, _ in FAVORITE_MODELS] and car['model'].lower() == 'x'):
            score += WEIGHTS['coolness_factor']

        # Adaptive Cruise Control
        if "no" not in car['warranty'].lower():
            score += WEIGHTS['warranty']
        
        if car["previous_owner"] == 1:
            score += car["previous_owner"]
        if car["previous_owner"] == 2:
            score += car["previous_owner"]*0.75

        if "no" in car["full_service_history"].lower():
            score -= 2
        
        if "no" in car["non_smoker_vehicle"].lower():
            score -= 1

        return score
    
    def rank_cars(self):
        """Score and rank all cars in the dataset"""
        self.data['score'] = self.data.apply(self.score_car, axis=1)
        return self.data.sort_values(by='score', ascending=False)

# Example Usage
# autoscorer = AutoScore('path/to/csv/folder')
# ranked_cars = autoscorer.rank_cars()
# print(ranked_cars[['make', 'model', 'score']].head(10))

