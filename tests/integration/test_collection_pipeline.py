import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch

from src.collection.google_play_adapter import GooglePlayAdapter
from src.storage.json_file_store import JsonFileStore
from src.collection.incremental_manager import IncrementalManager

@pytest.fixture
def pipeline():
    temp_dir = tempfile.mkdtemp()
    store = JsonFileStore(temp_dir)
    adapter = GooglePlayAdapter(max_retries=1, retry_backoff_seconds=0)
    manager = IncrementalManager(adapter, store)
    
    yield manager, store
    
    shutil.rmtree(temp_dir)

@patch('src.collection.google_play_adapter.reviews')
def test_end_to_end_collection(mock_reviews, pipeline):
    manager, store = pipeline
    app_id = "com.test.e2e"
    now = datetime.now()
    
    # Run 1: Fetch 2 reviews
    mock_reviews.return_value = ([
        {"reviewId": "r1", "at": now - timedelta(days=1), "content": "1", "score": 5},
        {"reviewId": "r2", "at": now - timedelta(days=2), "content": "2", "score": 4}
    ], None)
    
    result1 = manager.collect_new_reviews(app_id, now - timedelta(days=7), now, 100, "run1")
    assert len(result1.reviews) == 2
    
    # Check storage state
    processed = store.get_processed_review_ids(app_id)
    assert "r1" in processed
    assert "r2" in processed
    
    # Run 2: Fetch 3 reviews (2 old, 1 new)
    mock_reviews.return_value = ([
        {"reviewId": "r1", "at": now - timedelta(days=1), "content": "1", "score": 5},
        {"reviewId": "r2", "at": now - timedelta(days=2), "content": "2", "score": 4},
        {"reviewId": "r3", "at": now - timedelta(days=3), "content": "3", "score": 3}
    ], None)
    
    result2 = manager.collect_new_reviews(app_id, now - timedelta(days=7), now, 100, "run2")
    assert len(result2.reviews) == 1
    assert result2.reviews[0].review_id == "r3"
    
    processed = store.get_processed_review_ids(app_id)
    assert "r3" in processed
