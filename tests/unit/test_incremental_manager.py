import pytest
from unittest.mock import MagicMock
from datetime import datetime

from src.collection.incremental_manager import IncrementalManager
from src.models.review import CollectionResult, CollectionMetadata, RawReview
from src.models.enums import CollectionStatus

@pytest.fixture
def mock_adapter():
    return MagicMock()

@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.get_processed_review_ids.return_value = {"old_1"}
    return storage

@pytest.fixture
def manager(mock_adapter, mock_storage):
    return IncrementalManager(mock_adapter, mock_storage)

def test_collect_new_reviews(manager, mock_adapter, mock_storage):
    # Setup mock adapter to return a mix of old and new reviews
    mock_adapter.fetch_reviews.return_value = CollectionResult(
        reviews=[
            RawReview(review_id="old_1", app_id="test", source="test", review_text="a", star_rating=1, review_date=datetime.now(), collected_at=datetime.now()),
            RawReview(review_id="new_1", app_id="test", source="test", review_text="b", star_rating=1, review_date=datetime.now(), collected_at=datetime.now())
        ],
        metadata=CollectionMetadata(app_id="test", start_date=datetime.now(), end_date=datetime.now(), total_fetched=2, source="test", status=CollectionStatus.SUCCESS)
    )
    
    result = manager.collect_new_reviews("test", datetime.now(), datetime.now(), 100, "run1")
    
    # Should only return the new review
    assert len(result.reviews) == 1
    assert result.reviews[0].review_id == "new_1"
    
    # Storage should have been called to save the new review
    mock_storage.save_raw_reviews.assert_called_once()
    saved_reviews = mock_storage.save_raw_reviews.call_args[0][0]
    assert len(saved_reviews) == 1
    assert saved_reviews[0].review_id == "new_1"
    
def test_generate_stable_id(manager):
    review = RawReview(
        review_id="", # Empty ID
        app_id="test",
        source="test",
        reviewer_name="User",
        review_text="Text",
        star_rating=5,
        review_date=datetime(2026, 9, 1),
        collected_at=datetime.now()
    )
    
    stable_id = manager._generate_stable_id(review)
    assert stable_id is not None
    assert len(stable_id) == 64 # SHA-256 length
