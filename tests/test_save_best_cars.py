import os
import tempfile
import pandas as pd
import shutil
from auto_score import save_best_cars


def test_save_best_cars_creates_file_and_caps_rows():
    # Create a temporary directory to avoid overwriting real data
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "best_cars.csv")
        # Create a DataFrame with more than max_rows rows
        df = pd.DataFrame({
            "url": [f"url{i}" for i in range(500)],
            "score": [500 - i for i in range(500)],
        })
        save_best_cars(df, max_rows=100, best_cars_file=test_file)
        assert os.path.exists(test_file)
        loaded = pd.read_csv(test_file)
        assert len(loaded) == 100
        # Should be sorted by score descending
        assert loaded.iloc[0]["score"] >= loaded.iloc[-1]["score"]


def test_save_best_cars_deduplication():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "best_cars.csv")
        # First save
        df1 = pd.DataFrame({
            "url": ["url1", "url2"],
            "score": [10, 20],
        })
        save_best_cars(df1, max_rows=10, best_cars_file=test_file)
        # Second save with duplicate url1 but higher score
        df2 = pd.DataFrame({
            "url": ["url1", "url3"],
            "score": [30, 5],
        })
        save_best_cars(df2, max_rows=10, best_cars_file=test_file)
        loaded = pd.read_csv(test_file)
        # url1 should have score 30, url2 and url3 present
        assert set(loaded["url"]) == {"url1", "url2", "url3"}
        assert loaded[loaded["url"] == "url1"]["score"].iloc[0] == 30
