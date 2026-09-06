import pytest
from src.analysis.trend_analysis import TrendAnalysisService
from src.models.theme import ThemeResult, Theme, SentimentDistribution, TrendType, PrioritizedTheme
from src.models.pulse import WeeklyAggregate
from src.models.enums import Sentiment, SeverityLevel, PriorityLevel
from unittest.mock import MagicMock

@pytest.fixture
def current_theme_result():
    themes = [
        Theme(
            id="t1",
            name="App Crashes on Portfolio Open",
            description="App crashes",
            review_count=10,
            review_percentage=50.0,
            sentiment_distribution=SentimentDistribution(
                positive_count=0, neutral_count=0, negative_count=10, mixed_count=0,
                percentages={}
            ),
            product_area="trading",
            severity=SeverityLevel.HIGH,
            review_ids=["r1"]
        ),
        Theme(
            id="t2",
            name="Great New Features",
            description="Users love it",
            review_count=5,
            review_percentage=25.0,
            sentiment_distribution=SentimentDistribution(
                positive_count=5, neutral_count=0, negative_count=0, mixed_count=0,
                percentages={}
            ),
            product_area="core",
            severity=SeverityLevel.LOW,
            review_ids=["r2"]
        )
    ]
    return ThemeResult(themes=themes, unthemed_count=0)

@pytest.fixture
def historical_aggregate():
    old_theme = Theme(
        id="old_t1",
        name="App Crashes on Portfolio Open",
        description="App crashes",
        review_count=5,
        review_percentage=25.0,
        sentiment_distribution=SentimentDistribution(
            positive_count=0, neutral_count=0, negative_count=5, mixed_count=0,
            percentages={}
        ),
        product_area="trading",
        severity=SeverityLevel.HIGH,
        review_ids=["old1"]
    )
    
    mock_agg = MagicMock(spec=WeeklyAggregate)
    pt = PrioritizedTheme(theme=old_theme, priority=PriorityLevel.HIGH, score=0.8, factor_breakdown={}, rationale="")
    mock_agg.themes = [pt]
    return mock_agg

def test_trend_analysis_with_history(current_theme_result, historical_aggregate):
    mock_llm = MagicMock()
    mock_llm.analyze_json.side_effect = [
        {
            "interpretation": "Issue is getting worse",
            "recommendation": "Fix immediately"
        },
        {
            "interpretation": "Positive reception",
            "recommendation": "None"
        }
    ]
    
    service = TrendAnalysisService(llm_client=mock_llm)
    result = service.analyze_trends(current_theme_result, historical_aggregate)
    
    # Check that t1 was put into growing (volume went from 5 to 10, which is > 10% change)
    assert len(result.growing) == 1
    assert result.growing[0].theme.id == "t1"
    assert result.growing[0].volume_change_pct == 100.0  # (10-5)/5
    
    # Check that t2 is new
    assert len(result.new_themes) == 1
    assert result.new_themes[0].theme.id == "t2"
    assert result.new_themes[0].volume_change_pct is None

def test_trend_analysis_no_history(current_theme_result):
    mock_llm = MagicMock()
    mock_llm.analyze_json.return_value = {
        "interpretation": "Baseline",
        "recommendation": "Monitor"
    }
    
    service = TrendAnalysisService(llm_client=mock_llm)
    result = service.analyze_trends(current_theme_result, None)
    
    assert result.data_availability_note is not None
    assert "No historical data" in result.data_availability_note
    
    # Both should be in new_themes
    assert len(result.new_themes) == 2
    for signal in result.new_themes:
        assert signal.trend_type == TrendType.NEW
        assert signal.volume_change_pct is None
