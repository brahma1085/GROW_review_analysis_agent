import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.collection.google_play_adapter import GooglePlayAdapter
from src.models.enums import CollectionStatus

@pytest.fixture
def adapter():
    return GooglePlayAdapter(max_retries=1, retry_backoff_seconds=0)

def test_source_info(adapter):
    assert adapter.get_source_name() == "google_play"
    assert adapter.supports_incremental() == True

@patch('src.collection.google_play_adapter.reviews')
def test_fetch_reviews_success(mock_reviews, adapter):
    now = datetime.now()
    # Mock return: (list_of_reviews, continuation_token)
    mock_reviews.return_value = ([
        {
            "reviewId": "r1",
            "userName": "Test User",
            "content": "Good app",
            "score": 5,
            "at": now - timedelta(days=1)
        }
    ], None)
    
    start_date = now - timedelta(days=7)
    end_date = now
    
    result = adapter.fetch_reviews("com.test.app", start_date, end_date, 100)
    
    assert result.metadata.status == CollectionStatus.SUCCESS
    assert result.metadata.total_fetched == 1
    assert len(result.reviews) == 1
    assert result.reviews[0].review_id == "r1"
    assert result.reviews[0].star_rating == 5

@patch('src.collection.google_play_adapter.reviews')
def test_fetch_reviews_date_filtering(mock_reviews, adapter):
    now = datetime.now()
    # One review in range, one review older than start date
    mock_reviews.return_value = ([
        {
            "reviewId": "in_range",
            "at": now - timedelta(days=2)
        },
        {
            "reviewId": "too_old",
            "at": now - timedelta(days=10)
        }
    ], None)
    
    start_date = now - timedelta(days=7)
    end_date = now
    
    result = adapter.fetch_reviews("com.test.app", start_date, end_date, 100)
    
    assert len(result.reviews) == 1
    assert result.reviews[0].review_id == "in_range"

@patch('src.collection.google_play_adapter.reviews')
def test_fetch_reviews_error(mock_reviews, adapter):
    mock_reviews.side_effect = Exception("API Error")
    
    result = adapter.fetch_reviews("com.test.app", datetime.now(), datetime.now(), 100)
    
    assert result.metadata.status == CollectionStatus.FAILED
    assert len(result.errors) == 1
    assert result.errors[0].message == "API Error"
