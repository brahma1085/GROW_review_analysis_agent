import pytest
from datetime import datetime
from src.models.review import RawReview
from src.models.enums import Sentiment, PriorityLevel

def test_raw_review_validation():
    review_data = {
        "review_id": "123",
        "app_id": "com.test.app",
        "source": "google_play",
        "review_text": "Great app!",
        "star_rating": 5,
        "review_date": datetime.now(),
        "collected_at": datetime.now()
    }
    
    review = RawReview(**review_data)
    assert review.review_id == "123"
    assert review.star_rating == 5
    
def test_invalid_star_rating_type():
    review_data = {
        "review_id": "123",
        "app_id": "com.test.app",
        "source": "google_play",
        "review_text": "Great app!",
        "star_rating": "five", # Invalid type
        "review_date": datetime.now(),
        "collected_at": datetime.now()
    }
    
    with pytest.raises(ValueError):
        RawReview(**review_data)

def test_enums():
    assert Sentiment.POSITIVE == "positive"
    assert PriorityLevel.CRITICAL == "critical"
