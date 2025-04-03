EXCLUDED_CARS = {
    "volkswagen": ["caddy", "taigo"],
    "opel": ["astra", "corsa", "grandland x", "grandland", "crossland x", "crossland", "mokka"],
    "ford": ["puma", "fiesta"],
    "skoda": ["scala", "fabia"],
    "hyundai": ["kona", "i20", "nexo"],
    "toyota": ["c-hr"],
    "bmw": ["118"],
    "peugeot": ["208", "308"],
    "nissan": ["micra", "juke"],
    "renault": ["zoe", "clio"],
    "citroen": ["c3"],
    "kia": ["rio", "niro"],
    "dacia": ["logan", "sandero"],
    "seat": ["ibiza"],
}

# Define weight for each attribute
WEIGHTS = {
    "price": 4.5,
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

# Fuel type scores
FUEL_SCORES = {
    "Electric/Diesel": 1.0,
    "Electric/Gasoline": 0.9,
    "Diesel": 0.8,
    "Gasoline": 0.7,
    "Super 95": 0.7,
    "Regular/Benzine 91": 0.7
}

# Favorite make-model combinations for additional scoring
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
]

CSV_FILE_PATH = "data/makes_and_models.csv"
FILTER_MAKES = [
    "Volkswagen",
    "Mazda",
    "MG",
    "Tesla",
    "Land Rover",
    "Peugeot",
    "Fiat",
    "Citroen",
    "Chevrolet",
    "SEAT",
    "Daihatsu",
    "Porsche",
    "Jaguar",
    "Dacia",
    "Opel",
    "Volvo",
    "Ford",
    "Alfa Romeo",
    "Lotus",
    "Jeep",
    "Suzuki",
    "Hyundai",
    "Maserati",
    "Toyota",
    "BMW",
    "Renault",
    "Nissan",
    "Skoda",
    "MINI",
    "Kia",
    "Audi",
    "CUPRA",
    "Subaru",
    "Lancia",
    "Polestar",
    "Mercedes-Benz",
    "Mitsubishi",
    "Lexus",
]  # Add makes to include here