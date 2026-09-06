import pytest
from src.analysis.evidence_selection import EvidenceSelectionService
from src.models.theme import PrioritizedTheme, Theme, SentimentDistribution
from src.models.review import AnalyzedReview, NormalizedReview, RawReview
from src.models.enums import PriorityLevel, SeverityLevel, Sentiment, ReviewCategory
from datetime import datetime

@pytest.fixture
def mock_reviews():
    return {
        "r1": AnalyzedReview(
            normalized_review=NormalizedReview(
                original_review=RawReview(
                    review_id="r1", app_id="app", source="play", reviewer_name="User1",
                    review_text="This app is terrible because it always crashes when I open my portfolio. Please fix it.",
                    star_rating=1, review_date=datetime.now(), collected_at=datetime.now()
                ),
                original_text="This app is terrible because it always crashes when I open my portfolio. Please fix it.",
                cleaned_text="This app is terrible because it always crashes when I open my portfolio. Please fix it.",
                content_hash="h1", detected_language="en", is_usable=True
            ),
            sentiment=Sentiment.NEGATIVE, sentiment_confidence=0.9, categories=[],
            product_area="trading", severity=SeverityLevel.HIGH, intent="complaint", key_phrases=[]
        ),
        "r2": AnalyzedReview(
            normalized_review=NormalizedReview(
                original_review=RawReview(
                    review_id="r2", app_id="app", source="play", reviewer_name="User2",
                    review_text="Crashes.",
                    star_rating=1, review_date=datetime.now(), collected_at=datetime.now()
                ),
                original_text="Crashes.", cleaned_text="Crashes.", content_hash="h2", detected_language="en", is_usable=True
            ),
            sentiment=Sentiment.NEGATIVE, sentiment_confidence=0.9, categories=[],
            product_area="trading", severity=SeverityLevel.HIGH, intent="complaint", key_phrases=[]
        )
    }

@pytest.fixture
def mock_prioritized_themes():
    t1 = Theme(
        id="t1", name="Crashes", description="App crashes", review_count=2, review_percentage=100.0,
        sentiment_distribution=SentimentDistribution(positive_count=0, neutral_count=0, negative_count=2, mixed_count=0, percentages={}),
        product_area="trading", severity=SeverityLevel.HIGH, review_ids=["r1", "r2"]
    )
    return [PrioritizedTheme(theme=t1, priority=PriorityLevel.HIGH, score=0.8, factor_breakdown={}, rationale="")]

def test_evidence_selection(mock_prioritized_themes, mock_reviews):
    service = EvidenceSelectionService()
    
    # Needs a list of AnalyzedReview to pull from
    reviews_list = list(mock_reviews.values())
    
    result = service.select_evidence(
        prioritized_themes=mock_prioritized_themes,
        all_reviews=reviews_list,
        max_per_theme=1,
        max_overall=5
    )
    
    assert len(result.theme_evidence) == 1
    assert "t1" in result.theme_evidence
    assert len(result.theme_evidence["t1"]) == 1
    
    # It should select r1 because it's longer and more descriptive than r2
    excerpt = result.theme_evidence["t1"][0]
    assert excerpt.source_review_id == "r1"
    
    # Test top voice excerpts
    assert len(result.top_overall_voice) > 0
    assert result.top_overall_voice[0].source_review_id == "r1"

def test_evidence_selection_truncation(mock_prioritized_themes, mock_reviews):
    # Make r1 very long
    mock_reviews["r1"].normalized_review.original_text = "A " * 250
    mock_reviews["r1"].normalized_review.original_review.review_text = "A " * 250
    mock_reviews["r1"].normalized_review.cleaned_text = "A " * 250
    
    service = EvidenceSelectionService()
    result = service.select_evidence(
        prioritized_themes=mock_prioritized_themes,
        all_reviews=list(mock_reviews.values()),
        max_per_theme=1,
        max_overall=5
    )
    
    excerpt = result.theme_evidence["t1"][0]
    assert excerpt.is_truncated is True
    assert len(excerpt.displayed_text) < 500
    assert excerpt.displayed_text.endswith("...")
