"""Flask dashboard app for car scraping and notification."""

import os
import sys
import threading
import traceback
from flask import Flask, render_template, jsonify, request

# Add project root to sys.path for src imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=import-error,wrong-import-position
from src.config import Config
from src.table_utils import get_table_html
from src.scraper import Scraper
from src.exporter import Exporter
from src.auto_score import AutoScore
from src.notifier import Notifier

# Shared state for progress and results
dashboard_state = {"progress": 0, "details": "", "results": None, "scraping": False}
dashboard_state_lock = threading.Lock()

app = Flask(__name__)


def run_scrape():
    """Scrape and process car data for the dashboard."""

    with dashboard_state_lock:
        dashboard_state["scraping"] = True
        dashboard_state["progress"] = 0
        dashboard_state["details"] = "Loading configuration..."
    config = Config()
    with dashboard_state_lock:
        dashboard_state["progress"] = 5
        dashboard_state["details"] = "Starting scraping..."
    scraper = Scraper(config)
    with dashboard_state_lock:
        dashboard_state["progress"] = 10

    def progress_callback(page, total_pages):
        """Update progress during scraping."""
        current_progress = 10 + int(50 * page / total_pages)
        with dashboard_state_lock:
            dashboard_state["progress"] = min(current_progress, 60)
            dashboard_state["details"] = f"Scraping page {page}/{total_pages}"

    cars = scraper.scrape_data(
        sort_method="standard", progress_callback=progress_callback
    )
    with dashboard_state_lock:
        dashboard_state["progress"] = 60
        dashboard_state["details"] = "Exporting results for standard"
    exporter = Exporter(cars)
    exporter.export_to_csv("data/results/filtered_cars_standard.csv")
    with dashboard_state_lock:
        dashboard_state["progress"] = 80
        dashboard_state["details"] = "Analyzing data..."
    autoscorer = AutoScore("data/results")
    ranked_cars = autoscorer.rank_cars(n=20)
    with dashboard_state_lock:
        dashboard_state["results"] = ranked_cars
        dashboard_state["progress"] = 100
        dashboard_state["details"] = "Scrape complete!"
        dashboard_state["scraping"] = False


@app.route("/")
def index():
    """Render the dashboard index page."""
    return render_template("index.html")


@app.route("/start-scrape", methods=["POST"])
def start_scrape():
    """Start the scraping process in a background thread."""
    with dashboard_state_lock:
        if dashboard_state["scraping"]:
            return jsonify({"status": "already running"})
    t = threading.Thread(target=run_scrape)
    with dashboard_state_lock:
        dashboard_state["scrape_thread"] = t
    t.start()
    return jsonify({"status": "started"})


@app.route("/progress")
def progress():
    """Return the current scraping progress."""
    with dashboard_state_lock:
        return jsonify(
            {
                "progress": dashboard_state["progress"],
                "details": dashboard_state["details"],
                "scraping": dashboard_state["scraping"],
            }
        )


@app.route("/results")
def results():
    """Return the HTML table of results or a message if none."""
    with dashboard_state_lock:
        df = dashboard_state["results"]
    if df is None:
        return "<p>No results yet.</p>"
    html = get_table_html(df.head(20))
    return html


@app.route("/all-time-bests")
def all_time_bests():
    """Return the HTML table of all-time best cars."""
    try:
        autoscorer = AutoScore("data/results")
        bests = autoscorer.get_all_time_best(n=20)
        html = get_table_html(bests)
        return html
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"<p>Error: {e}</p>"


@app.route("/config", methods=["GET"])
def get_config():
    """Return the current configuration for the dashboard."""
    config = Config()
    filters = config.get_filters_for_frontend()
    return jsonify(
        {
            "filters": filters,
            "num_pages": config.num_pages,
            "scoring_profiles": config.scoring_profiles,
            "excluded_cars": config.excluded_cars,
        }
    )


@app.route("/config", methods=["POST"])
def set_config():
    """Update the dashboard configuration."""
    data = request.get_json()
    config = Config()
    if "filters" in data:
        config.filters = config.set_filters_from_frontend(data["filters"])
    if "num_pages" in data:
        config.num_pages = data["num_pages"]
    if "scoring_profiles" in data:
        config.scoring_profiles = data["scoring_profiles"]
    if "excluded_cars" in data:
        config.excluded_cars = data["excluded_cars"]
    config.save()
    return jsonify({"status": "success"})


@app.route("/notify", methods=["POST"])
def notify():
    """Send an email notification with the latest results."""
    # Only catch exceptions for email sending, not for the whole route
    with dashboard_state_lock:
        ranked_cars = dashboard_state["results"]
    if ranked_cars is None:
        return jsonify({"status": "error", "error": "No results to send."})
    config = Config()
    notifier = Notifier(config)
    try:
        notifier.send_email("Latest Car Listings", ranked_cars)
    except (  # Catching all exceptions for email sending is intentional
        Exception  #  pylint: disable=broad-exception-caught
    ) as e:
        print(f"Failed to send email: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "error": str(e)})
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
