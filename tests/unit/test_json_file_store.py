import tempfile
import shutil
import pytest
from pathlib import Path
from datetime import datetime

from src.storage.json_file_store import JsonFileStore
from src.models.review import RawReview
from src.models.pulse import WeeklyAggregate, WeekMetrics
from src.models.theme import SentimentDistribution

@pytest.fixture
def temp_store():
    temp_dir = tempfile.mkdtemp()
    store = JsonFileStore(temp_dir)
    yield store
    shutil.rmtree(temp_dir)

def test_ensure_directories(temp_store):
    dirs = ["raw", "normalized", "analysis", "themes", "aggregates", "collection", "pulses", "logs"]
    for d in dirs:
        assert (temp_store.data_dir / d).exists()

def test_save_raw_reviews(temp_store):
    reviews = [
        RawReview(
            review_id="1",
            app_id="test_app",
            source="test",
            review_text="Test",
            star_rating=5,
            review_date=datetime.now(),
            collected_at=datetime.now()
        )
    ]
    temp_store.save_raw_reviews(reviews, "run_1")
    filepath = temp_store._get_path("raw", "test_app", "run_1_raw_reviews.json")
    assert filepath.exists()

def test_save_and_get_weekly_aggregate(temp_store):
    metrics = WeekMetrics(
        reviews_analyzed=10,
        avg_star_rating=4.5,
        sentiment_distribution=SentimentDistribution(),
        theme_count=2,
        emerging_count=0,
        critical_high_count=0
    )
    agg = WeeklyAggregate(
        run_id="run_agg_1",
        app_id="test_app",
        period_start=datetime.now(),
        period_end=datetime.now(),
        metrics=metrics
    )
    temp_store.save_weekly_aggregate(agg)
    
    loaded_agg = temp_store.get_previous_aggregate("test_app", periods_back=1)
    assert loaded_agg is not None
    assert loaded_agg.run_id == "run_agg_1"
    assert loaded_agg.metrics.reviews_analyzed == 10
