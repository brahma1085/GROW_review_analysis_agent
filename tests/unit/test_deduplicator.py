import pytest
from datetime import datetime
from src.processing.deduplicator import ReviewDeduplicator
from src.models.review import NormalizedReview, RawReview

def create_normalized(id: str, text: str, hash_val: str) -> NormalizedReview:
    raw = RawReview(
        review_id=id,
        app_id="test",
        source="test",
        review_text=text,
        star_rating=5,
        review_date=datetime.now(),
        collected_at=datetime.now()
    )
    return NormalizedReview(
        original_review=raw,
        original_text=text,
        cleaned_text=text,
        detected_language="en",
        is_usable=True,
        content_hash=hash_val
    )

@pytest.fixture
def deduplicator():
    return ReviewDeduplicator(exact_match=True, near_duplicate_threshold=0.85)

def test_exact_deduplication(deduplicator):
    reviews = [
        create_normalized("1", "Great app", "hash1"),
        create_normalized("2", "Great app", "hash1"),
        create_normalized("3", "Terrible app", "hash2")
    ]
    
    result = deduplicator.deduplicate(reviews)
    assert len(result.unique_reviews) == 2
    assert result.removed_count == 1
    assert result.details[0].reason == "exact"
    assert result.details[0].review_id == "2"

def test_near_deduplication(deduplicator):
    reviews = [
        create_normalized("1", "This is a very good app indeed", "hash1"),
        create_normalized("2", "This is a very good app indeed!", "hash2"), # High similarity
        create_normalized("3", "I absolutely hate this garbage", "hash3")
    ]
    
    result = deduplicator.deduplicate(reviews)
    assert len(result.unique_reviews) == 2
    assert result.removed_count == 1
    assert result.details[0].reason == "near_duplicate"

def test_cross_period_deduplication(deduplicator):
    reviews = [
        create_normalized("1", "New review", "hash1"),
        create_normalized("2", "Old review", "hash2")
    ]
    
    historical = {"hash2"}
    
    result = deduplicator.deduplicate(reviews, historical_ids=historical)
    assert len(result.unique_reviews) == 1
    assert result.unique_reviews[0].original_review.review_id == "1"
    assert result.removed_count == 1
    assert result.details[0].reason == "historical"
