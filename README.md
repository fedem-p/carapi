# carapi

A Python-based car listing scraper and analyzer for Autoscout24. This project scrapes, processes, and analyzes car listing data with automated scoring, deduplication, and email notifications.

## 🚗 Features

- **Web Scraping**: Automated scraping of car listings from Autoscout24
- **Data Processing**: Clean, normalize, and deduplicate car data
- **Intelligent Scoring**: Score cars based on price, mileage, year, and other factors
- **Email Notifications**: Automated email reports with top-rated cars
- **Dashboard Interface**: Web-based dashboard for configuration and monitoring
- **Export Capabilities**: CSV export/import functionality
- **Comprehensive Testing**: 90%+ test coverage with unit and integration tests

## 🏗️ Architecture

The project follows a modular architecture with clear separation of concerns:

```
src/
├── main.py              # Main entry point and workflow orchestration
├── scraper.py           # Web scraping logic for Autoscout24
├── auto_score.py        # Car scoring and ranking algorithms  
├── config.py            # Configuration management
├── exporter.py          # CSV export/import functionality
├── notifier.py          # Email notification system
├── table_utils.py       # HTML table generation utilities
├── fetch_makes_and_models.py  # Car make/model data management
└── constants.py         # Application constants

dashboard/
└── app.py               # Flask web dashboard

tests/                   # Comprehensive test suite (71 tests, 90% coverage)
data/                    # Input data and results storage
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker (optional, for containerized deployment)

### Installation

#### Local Development with Poetry

1. **Install Poetry** (if not already installed):
   ```bash
   pip install poetry
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/fedem-p/carapi.git
   cd carapi
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Activate the Poetry shell**:
   ```bash
   poetry shell
   ```

#### Docker Installation

1. **Build the container**:
   ```bash
   docker build -t autoscout_scraper .
   ```

2. **Run with Docker Compose**:
   ```bash
   docker compose build && docker compose up
   ```

## 🔧 Configuration

### Environment Variables

Configure the application using environment variables:

```bash
# Email Configuration (required for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=recipient@gmail.com

# Application Settings
SEND_EMAIL=false  # Set to 'true' to enable email notifications
```

### Configuration File

The application uses `settings.json` for runtime configuration:

```json
{
  "filters": {
    "body": ["1", "2"],           # Body types (1=Compact, 2=Convertible, etc.)
    "fuel": ["B", "D"],           # Fuel types (B=Gasoline, D=Diesel, etc.)
    "sort": "price",              # Sort method: standard|price|age
    "min_power": "100"            # Minimum power in kW
  },
  "num_pages": 10,                # Number of pages to scrape
  "scoring_profiles": {
    "standard": {
      "weights": {
        "price": 1,               # Weight for price factor
        "mileage": 1,             # Weight for mileage factor
        "year": 1                 # Weight for year factor
      }
    }
  },
  "excluded_cars": {
    "brand": ["model1", "model2"] # Cars to exclude from results
  }
}
```

## 📖 Usage

### Basic Usage

1. **Run the main scraping workflow**:
   ```bash
   poetry run python -m src.main
   ```

2. **With email notifications**:
   ```bash
   poetry run python -m src.main --email
   ```

3. **Using environment variable for email**:
   ```bash
   SEND_EMAIL=true poetry run python -m src.main
   ```

### Common Workflows

#### 1. Scraping and Analysis
```bash
# Basic scraping with multiple sort methods
poetry run python -m src.main

# This will:
# - Scrape car listings with 3 different sort methods (standard, price, age)
# - Export results to CSV files in data/results/
# - Analyze and rank cars using the scoring algorithm
# - Display top 20 cars with scores and grades
```

#### 2. Update Car Makes and Models
```bash
# Refresh the car makes/models database
poetry run bash ./update_make_models.sh

# Or with Docker:
docker run --rm -v $(pwd):/app autoscout_scraper bash ./update_make_models.sh
```

#### 3. Dashboard Interface
The application includes a web dashboard for configuration and monitoring:
```bash
# Start the dashboard (usually runs automatically with docker-compose)
cd dashboard && python app.py
```

### Advanced Usage

#### Custom Scoring Profiles
Modify the scoring algorithm by updating `settings.json`:

```json
{
  "scoring_profiles": {
    "price_focused": {
      "weights": {
        "price": 3,     # Higher weight for price
        "mileage": 1,
        "year": 1
      }
    },
    "low_mileage": {
      "weights": {
        "price": 1,
        "mileage": 3,   # Higher weight for mileage
        "year": 1
      }
    }
  }
}
```

#### Filtering and Exclusions
Configure filtering in `settings.json`:

```json
{
  "filters": {
    "body": ["1", "2", "3"],      # Multiple body types
    "fuel": ["B"],                # Only gasoline cars
    "min_power": "150"            # Minimum 150kW power
  },
  "excluded_cars": {
    "Ford": ["Focus", "Fiesta"],  # Exclude specific models
    "Volkswagen": ["Polo"]
  }
}
```

## 🧪 Development and Testing

### Running Tests

```bash
# Run all tests with coverage
bash ./test.sh

# Or manually:
poetry run python -m pytest --cov=src --cov-report=html tests/

# Run specific test files
poetry run python -m pytest tests/test_scraper.py -v

# View coverage report
open htmlcov/index.html
```

### Linting and Code Quality

```bash
# Run linting
bash ./lint.sh

# Or manually:
poetry run pylint src
poetry run mypy src
```

### Test Structure

The project includes comprehensive tests with 90%+ coverage:

- **Unit Tests**: Individual module testing
- **Integration Tests**: End-to-end workflow testing  
- **Mock Testing**: External dependencies (email, HTTP requests)
- **Edge Cases**: Error handling and boundary conditions

## 📊 Output and Results

### Data Export

The application exports data to several formats:

- **CSV Files**: `data/results/filtered_cars_{sort_method}.csv`
- **Best Cars**: `data/best/best_cars.csv` (deduplicated top cars)
- **Coverage Reports**: `htmlcov/index.html`

### Scoring System

Cars are scored based on multiple factors:

- **Price Score**: Lower prices get higher scores
- **Mileage Score**: Lower mileage gets higher scores  
- **Year Score**: Newer cars get higher scores
- **Final Score**: Weighted combination of all factors

**Grade Mapping**:
- 🥇 Outstanding: 28-30 points
- 🥈 Excellent: 25-27 points
- 🥉 Good: 20-24 points
- ✅ Decent: 15-19 points
- ⚠️ Not Good: 10-14 points
- ❌ Bad: 0-9 points

### Email Reports

When enabled, email reports include:
- HTML table with top-ranked cars
- Car images and direct links to listings
- Highlighted cars with exceptional scores
- Formatted data for easy review

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the Poetry shell (`poetry shell`)
2. **Email Not Sending**: Check SMTP credentials and firewall settings
3. **No Results**: Verify filters aren't too restrictive
4. **Memory Issues**: Reduce `num_pages` in configuration

### Environment Issues

If you encounter environment problems:
```bash
# Reset Poetry environment
rm -rf .venv
poetry install

# Rebuild Docker container  
docker compose down
docker compose build --no-cache
docker compose up
```

### Debug Mode

Enable detailed logging by modifying the logging level in the source code or setting environment variables.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`bash ./test.sh`)
6. Run linting (`bash ./lint.sh`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Style

- Follow PEP 8 style guidelines
- Add docstrings to all public functions and classes
- Maintain test coverage above 90%
- Use type hints where appropriate

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for educational and research purposes
- Uses Autoscout24 for car listing data
- Powered by Python, BeautifulSoup, Pandas, and Flask

---

**Note**: This tool is for educational purposes. Please respect website terms of service and implement appropriate rate limiting when scraping.