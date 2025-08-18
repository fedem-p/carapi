from flask import Flask, render_template, jsonify, request
import threading
import time
import pandas as pd
import sys
import os

# Add project root to sys.path for src imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Shared state for progress and results
dashboard_state = {
    'progress': 0,
    'details': '',
    'results': None,
    'scraping': False
}

dashboard_state_lock = threading.Lock()

app = Flask(__name__)

# Scrape and process car data for the dashboard
def run_scrape():
    from src.config import Config
    from src.scraper import Scraper
    from src.exporter import Exporter
    from src.auto_score import AutoScore
    with dashboard_state_lock:
        dashboard_state['scraping'] = True
        dashboard_state['progress'] = 0
        dashboard_state['details'] = 'Loading configuration...'
    config = Config()
    with dashboard_state_lock:
        dashboard_state['progress'] = 5
        dashboard_state['details'] = 'Starting scraping...'
    scraper = Scraper(config)
    with dashboard_state_lock:
        dashboard_state['progress'] = 10

    def progress_callback(page, total_pages):
        progress = 10 + int(50 * page / total_pages)
        with dashboard_state_lock:
            dashboard_state['progress'] = min(progress, 60)
            dashboard_state['details'] = f'Scraping page {page}/{total_pages}'

    cars = scraper.scrape_data(sort_method="standard", progress_callback=progress_callback)
    with dashboard_state_lock:
        dashboard_state['progress'] = 60
        dashboard_state['details'] = f'Exporting results for standard'
    exporter = Exporter(cars)
    exporter.export_to_csv(f"data/results/filtered_cars_standard.csv")
    with dashboard_state_lock:
        dashboard_state['progress'] = 80
        dashboard_state['details'] = 'Analyzing data...'
    autoscorer = AutoScore("data/results")
    ranked_cars = autoscorer.rank_cars(n=20)
    with dashboard_state_lock:
        dashboard_state['results'] = ranked_cars
        dashboard_state['progress'] = 100
        dashboard_state['details'] = 'Scrape complete!'
        dashboard_state['scraping'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-scrape', methods=['POST'])
def start_scrape():
    with dashboard_state_lock:
        if dashboard_state['scraping']:
            return jsonify({'status': 'already running'})
    t = threading.Thread(target=run_scrape)
    with dashboard_state_lock:
        dashboard_state['scrape_thread'] = t
    t.start()
    return jsonify({'status': 'started'})

@app.route('/progress')
def progress():
    with dashboard_state_lock:
        return jsonify({
            'progress': dashboard_state['progress'],
            'details': dashboard_state['details'],
            'scraping': dashboard_state['scraping']
        })

@app.route('/results')
def results():
    from src.table_utils import get_table_html
    with dashboard_state_lock:
        df = dashboard_state['results']
    if df is None:
        return '<p>No results yet.</p>'
    html = get_table_html(df.head(20))
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
