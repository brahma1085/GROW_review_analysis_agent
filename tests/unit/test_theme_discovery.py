import pytest
import json
from unittest.mock import MagicMock
from src.analysis.theme_discovery import ThemeDiscoveryService
from src.models.review import AnalyzedReview, NormalizedReview, RawReview
from src.models.enums import Sentiment, SeverityLevel, ReviewCategory
from datetime import datetime

@pytest.fixture
def sample_analyzed_reviews():
    r1 = AnalyzedReview(
        normalized_review=NormalizedReview(
            original_review=RawReview(
                review_id="r1",
                app_id="app",
                source="play_store",
                reviewer_name="User",
                review_text="App crashes on open",
                star_rating=1,
                review_date=datetime.now(),
                collected_at=datetime.now()
            ),
            original_text="App crashes on open",
            cleaned_text="App crashes on open",
            content_hash="h1", detected_language="en", is_usable=True
        ),
        sentiment=Sentiment.NEGATIVE,
        sentiment_confidence=0.9,
        categories=[ReviewCategory.BUG_REPORT],
        product_area="trading",
        severity=SeverityLevel.HIGH,
        intent="report_bug",
        key_phrases=["crashes on open"]
    )
    
    r2 = AnalyzedReview(
        normalized_review=NormalizedReview(
            original_review=RawReview(
                review_id="r2",
                app_id="app",
                source="play_store",
                reviewer_name="User",
                review_text="Great app",
                star_rating=5,
                review_date=datetime.now(),
                collected_at=datetime.now()
            ),
            original_text="Great app",
            cleaned_text="Great app",
            content_hash="h2", detected_language="en", is_usable=True
        ),
        sentiment=Sentiment.POSITIVE,
        sentiment_confidence=0.95,
        categories=[ReviewCategory.PRAISE],
        product_area="trading",
        severity=SeverityLevel.LOW,
        intent="praise",
        key_phrases=["Great app"]
    )
    return [r1, r2]

def test_theme_discovery(sample_analyzed_reviews):
    mock_llm = MagicMock()
    mock_llm.analyze_batch_json.return_value = {
        "themes": [
            {
                "id": "t1",
                "name": "App Crashes",
                "description": "App is crashing",
                "review_ids": ["r1"]
            }
        ],
        "unthemed_review_ids": ["r2"]
    }
    
    service = ThemeDiscoveryService(llm_client=mock_llm)
    result = service.discover_themes(sample_analyzed_reviews)
    
    assert len(result.themes) == 1
    assert result.themes[0].name == "App Crashes"
    assert result.themes[0].review_count == 1
    assert result.themes[0].sentiment_distribution.negative_count == 1
    assert result.themes[0].sentiment_distribution.positive_count == 0
    assert result.themes[0].product_area == "trading"
    assert result.themes[0].severity == SeverityLevel.HIGH
    assert result.unthemed_count == 1

def test_theme_discovery_llm_failure(sample_analyzed_reviews):
    mock_llm = MagicMock()
    mock_llm.analyze_batch_json.side_effect = Exception("LLM Error")
    
    service = ThemeDiscoveryService(llm_client=mock_llm)
    result = service.discover_themes(sample_analyzed_reviews)
    
    assert len(result.themes) == 0
    assert result.unthemed_count == 2
