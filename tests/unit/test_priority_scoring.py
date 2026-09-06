import pytest
from src.analysis.priority_scoring import PriorityScoringService
from src.models.theme import Theme, SentimentDistribution, TrendSignal, TrendType, ThemeResult
from src.models.enums import SeverityLevel, PriorityLevel

@pytest.fixture
def mock_config():
    return {
        "weights": {
            "frequency": 0.20,
            "sentiment": 0.20,
            "severity": 0.15,
            "recency": 0.10,
            "growth": 0.15,
            "breadth": 0.10,
            "business_impact": 0.10
        },
        "thresholds": {
            "critical": 0.8,
            "high": 0.6,
            "medium": 0.4
        }
    }

@pytest.fixture
def sample_theme():
    return Theme(
        id="t1",
        name="App Crashes",
        description="App is crashing",
        review_count=100,
        review_percentage=50.0,
        sentiment_distribution=SentimentDistribution(
            positive_count=0, neutral_count=0, negative_count=100, mixed_count=0,
            percentages={"positive": 0.0, "neutral": 0.0, "negative": 100.0, "mixed": 0.0}
        ),
        product_area="trading",
        severity=SeverityLevel.CRITICAL,
        review_ids=["r1"]
    )

@pytest.fixture
def sample_trend_signal(sample_theme):
    return TrendSignal(
        theme=sample_theme,
        trend_type=TrendType.GROWING,
        evidence="Growing fast",
        interpretation="Urgent",
        recommendation="Fix",
        volume_change_pct=50.0,
        sentiment_change=None
    )

def test_priority_scoring(mock_config, sample_theme, sample_trend_signal):
    service = PriorityScoringService(mock_config)
    
    # 100 reviews out of a hypothetical total of 200
    theme_result = ThemeResult(themes=[sample_theme])
    from src.models.theme import TrendResult
    trend_result = TrendResult(growing=[sample_trend_signal])

    prioritized = service.score_themes(
        theme_result=theme_result,
        trend_result=trend_result
    )
    
    assert len(prioritized) == 1
    pt = prioritized[0]
    
    # Check factor breakdown calculation
    assert "frequency" in pt.factor_breakdown
    assert "severity_language" in pt.factor_breakdown
    assert "growth" in pt.factor_breakdown
    
    # Just check that priority score is calculated successfully
    assert pt.score > 0
    assert pt.priority in [PriorityLevel.HIGH, PriorityLevel.CRITICAL]

def test_priority_scoring_no_trend(mock_config, sample_theme):
    service = PriorityScoringService(mock_config)
    
    theme_result = ThemeResult(themes=[sample_theme])
    from src.models.theme import TrendResult
    trend_result = TrendResult()

    prioritized = service.score_themes(
        theme_result=theme_result,
        trend_result=trend_result
    )
    
    pt = prioritized[0]
    assert pt.factor_breakdown["growth"] == 0.0
