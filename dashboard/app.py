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

app = Flask(__name__)

# Dummy scrape function (replace with real logic)
def run_scrape():
    from src.config import Config
    from src.scraper import Scraper
    from src.exporter import Exporter
    from src.auto_score import AutoScore
    dashboard_state['scraping'] = True
    dashboard_state['progress'] = 0
    dashboard_state['details'] = 'Loading configuration...'
    config = Config()
    dashboard_state['progress'] = 5
    dashboard_state['details'] = 'Starting scraping...'
    scraper = Scraper(config)
    dashboard_state['progress'] = 10

    def progress_callback(page, total_pages):
        # Progress: 10% (start), 60% (end of scraping)
        progress = 10 + int(50 * page / total_pages)
        dashboard_state['progress'] = min(progress, 60)
        dashboard_state['details'] = f'Scraping page {page}/{total_pages}'

    cars = scraper.scrape_data(sort_method="standard", progress_callback=progress_callback)
    dashboard_state['progress'] = 60
    dashboard_state['details'] = f'Exporting results for standard'
    exporter = Exporter(cars)
    exporter.export_to_csv(f"data/results/filtered_cars_standard.csv")
    dashboard_state['progress'] = 80
    dashboard_state['details'] = 'Analyzing data...'
    autoscorer = AutoScore("data/results")
    ranked_cars = autoscorer.rank_cars(n=20)
    dashboard_state['results'] = ranked_cars
    dashboard_state['progress'] = 100
    dashboard_state['details'] = 'Scrape complete!'
    dashboard_state['scraping'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-scrape', methods=['POST'])
def start_scrape():
    if dashboard_state['scraping']:
        return jsonify({'status': 'already running'})
    t = threading.Thread(target=run_scrape)
    t.start()
    return jsonify({'status': 'started'})

@app.route('/progress')
def progress():
    return jsonify({
        'progress': dashboard_state['progress'],
        'details': dashboard_state['details'],
        'scraping': dashboard_state['scraping']
    })

@app.route('/results')
def results():
    df = dashboard_state['results']
    if df is None:
        return '<p>No results yet.</p>'
    # Import get_table_html from your notifier
    from src.notifier import Notifier
    # Dummy config for Notifier (not used for table)
    class DummyConfig:
        email_settings = {'username': '', 'recipient': '', 'smtp_server': '', 'smtp_port': '', 'password': ''}
    notifier = Notifier(DummyConfig())
    html = notifier.get_table_html(df.head(20))
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
